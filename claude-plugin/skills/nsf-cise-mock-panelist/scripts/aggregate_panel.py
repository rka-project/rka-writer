#!/usr/bin/env python3
"""Aggregate frozen mock-panel reviews without making a semantic panel decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RATING_VALUES = {"excellent": 5, "very_good": 4, "good": 3, "fair": 2, "poor": 1}
DIMENSION_VALUES = {"strong": 3, "adequate": 2, "weak": 1}
SEVERITY_VALUES = {"minor": 1, "moderate": 2, "major": 3, "blocker": 4}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="append", required=True, help="Individual review JSON; repeatable")
    parser.add_argument("--output", required=True)
    parser.add_argument("--minimum-reviews", type=int, default=1)
    return parser.parse_args()


def aggregate_reviews(
    reviews: list[tuple[Path, dict[str, Any]]], *, generated_at: str
) -> dict[str, Any]:
    """Return the deterministic aggregate for already validated review records."""

    reviews = sorted(
        reviews,
        key=lambda item: (str(item[1].get("reviewer_id", "")), str(item[0])),
    )
    proposal_ids = {str(review.get("proposal_id", "")).strip() for _, review in reviews}
    reviewer_ids = [str(review.get("reviewer_id", "")) for _, review in reviews]
    review_hashes = {
        str(review["reviewer_id"]): sha256_file(path) for path, review in reviews
    }
    rating_counts: Counter[str] = Counter()
    rating_numbers: list[int] = []
    confidence_counts: Counter[str] = Counter()
    independence_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    profile_counts: Counter[str] = Counter()
    issue_occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    dimension_entries: dict[str, list[dict[str, str]]] = defaultdict(list)

    for _, review in reviews:
        rating = review["rating"]
        value = str(rating.get("value", "unrated"))
        rating_counts[value] += 1
        if value in RATING_VALUES:
            rating_numbers.append(RATING_VALUES[value])
        confidence_counts[str(rating.get("confidence", "unreported"))] += 1
        independence_counts[str(review.get("review_independence", "unreported"))] += 1
        family_counts[str(review.get("reviewer_family", "unreported"))] += 1
        profile = review.get("reviewer_profile")
        if isinstance(profile, dict):
            profile_counts[str(profile.get("profile_id", "unreported"))] += 1
        else:
            profile_counts["unreported"] += 1

        for finding in review["findings"]:
            if not isinstance(finding, dict):
                continue
            issue_key = str(finding.get("issue_key", "")).strip()
            if issue_key:
                issue_occurrences[issue_key].append(
                    {
                        "reviewer_id": str(review["reviewer_id"]),
                        "finding_id": str(finding.get("id", "")),
                        "severity": str(finding.get("severity", "")),
                        "stance": str(finding.get("stance", "")),
                    }
                )

        for name, entry in review["dimensions"].items():
            if isinstance(entry, dict):
                dimension_entries[str(name)].append(
                    {
                        "reviewer_id": str(review["reviewer_id"]),
                        "assessment": str(entry.get("assessment", "not_assessable")),
                    }
                )

    disagreements: list[dict[str, Any]] = []
    if rating_numbers and max(rating_numbers) - min(rating_numbers) >= 2:
        disagreements.append(
            {
                "topic": "overall_rating",
                "kind": "material_spread",
                "positions": {
                    str(review["reviewer_id"]): review.get("rating", {}).get(
                        "value", "unrated"
                    )
                    for _, review in reviews
                },
            }
        )

    dimension_summary: dict[str, Any] = {}
    for name, entries in sorted(dimension_entries.items()):
        values = [
            DIMENSION_VALUES[item["assessment"]]
            for item in entries
            if item["assessment"] in DIMENSION_VALUES
        ]
        dimension_summary[name] = {
            "positions": entries,
            "assessment_counts": dict(Counter(item["assessment"] for item in entries)),
        }
        if values and max(values) - min(values) >= 2:
            disagreements.append(
                {
                    "topic": f"dimension:{name}",
                    "kind": "material_spread",
                    "positions": entries,
                }
            )

    recurring = {
        key: occurrences
        for key, occurrences in sorted(issue_occurrences.items())
        if len({item["reviewer_id"] for item in occurrences}) >= 2
    }
    isolated = {
        key: occurrences
        for key, occurrences in sorted(issue_occurrences.items())
        if len({item["reviewer_id"] for item in occurrences}) == 1
    }

    corroborated: dict[str, list[dict[str, str]]] = {}
    contested: dict[str, list[dict[str, str]]] = {}
    for key, occurrences in recurring.items():
        stances = {item["stance"] for item in occurrences}
        severities = [
            SEVERITY_VALUES[item["severity"]]
            for item in occurrences
            if item["severity"] in SEVERITY_VALUES
        ]
        if len(stances) == 1:
            corroborated[key] = occurrences
        else:
            contested[key] = occurrences
            disagreements.append(
                {
                    "topic": f"issue:{key}",
                    "kind": "stance_conflict",
                    "positions": occurrences,
                }
            )
        if severities and max(severities) - min(severities) >= 2:
            disagreements.append(
                {
                    "topic": f"issue:{key}",
                    "kind": "severity_spread",
                    "positions": occurrences,
                }
            )

    return {
        "schema_version": "1.1",
        "proposal_id": next(iter(proposal_ids)),
        "generated_at": generated_at,
        "reviewers": reviewer_ids,
        "review_files": [str(path) for path, _ in reviews],
        "review_hashes": review_hashes,
        "rating_distribution": dict(rating_counts),
        "confidence_distribution": dict(confidence_counts),
        "review_independence_distribution": dict(independence_counts),
        "reviewer_family_distribution": dict(family_counts),
        "simulated_reviewer_profile_distribution": dict(profile_counts),
        "dimensions": dimension_summary,
        "recurring_issue_keys": recurring,
        "corroborated_issue_keys": corroborated,
        "contested_issue_keys": contested,
        "single_reviewer_issue_keys": isolated,
        "disagreements_requiring_chair_review": disagreements,
        "notice": "Mechanical aggregation only; recurrence is not truth and a rating distribution is not an internal mock disposition.",
    }


def main() -> int:
    args = parse_args()
    try:
        reviews = [(Path(path).resolve(), load_json(Path(path).resolve())) for path in args.review]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.minimum_reviews < 1:
        print("error: --minimum-reviews must be at least 1", file=sys.stderr)
        return 2
    if len(reviews) < args.minimum_reviews:
        print(
            f"error: received {len(reviews)} reviews; at least {args.minimum_reviews} required",
            file=sys.stderr,
        )
        return 2

    reviewer_ids = [str(review.get("reviewer_id", "")) for _, review in reviews]
    if any(not reviewer_id for reviewer_id in reviewer_ids) or len(reviewer_ids) != len(set(reviewer_ids)):
        print("error: reviewer_id values must be present and unique", file=sys.stderr)
        return 2

    proposal_ids = {str(review.get("proposal_id", "")).strip() for _, review in reviews}
    if "" in proposal_ids or len(proposal_ids) != 1:
        print("error: all reviews must have one matching, non-empty proposal_id", file=sys.stderr)
        return 2

    for path, review in reviews:
        if review.get("schema_version") != "1.1":
            print(f"error: invalid schema_version in {path}", file=sys.stderr)
            return 2
        rating = review.get("rating")
        findings = review.get("findings")
        dimensions = review.get("dimensions")
        if not isinstance(rating, dict) or rating.get("value") not in {*RATING_VALUES, "unrated"}:
            print(f"error: invalid rating object in {path}; run the review gate first", file=sys.stderr)
            return 2
        if not isinstance(findings, list) or not isinstance(dimensions, dict):
            print(f"error: malformed findings/dimensions in {path}; run the review gate first", file=sys.stderr)
            return 2

    payload = aggregate_reviews(reviews, generated_at=utc_now())
    output = Path(args.output).expanduser().resolve()
    protected = {path for path, _ in reviews}
    if output in protected:
        print("error: --output cannot overwrite a frozen review", file=sys.stderr)
        return 2
    if output.exists():
        for review_path in protected:
            try:
                if os.path.samefile(output, review_path):
                    print("error: --output cannot alias a frozen review", file=sys.stderr)
                    return 2
            except OSError:
                continue
    atomic_write(output, payload)
    disagreement_count = len(payload["disagreements_requiring_chair_review"])
    print(f"wrote {output} ({len(reviews)} reviews, {disagreement_count} flagged disagreements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
