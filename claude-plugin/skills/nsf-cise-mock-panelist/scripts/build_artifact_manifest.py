#!/usr/bin/env python3
"""Hash-pin every required artifact from a completed mock-panel run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from protocol_digest import protocol_bundle_sha256
from schema_contract import validate_instance


FULL_PANEL_FILES = {
    "authority_snapshot": "authority-snapshot.md",
    "compliance_screen": "compliance-screen.md",
    "review_r1_markdown": "review-r1.md",
    "review_r1_json": "review-r1.json",
    "review_r2_markdown": "review-r2.md",
    "review_r2_json": "review-r2.json",
    "review_r3_markdown": "review-r3.md",
    "review_r3_json": "review-r3.json",
    "novelty_audit": "novelty-audit.md",
    "methods_audit": "methods-audit.md",
    "broader_impacts_audit": "broader-impacts-audit.md",
    "presentation_audit": "presentation-audit.md",
    "kill_argument": "kill-argument.md",
    "kill_adjudication": "kill-adjudication.md",
    "issue_ledger": "issue-ledger.jsonl",
    "pre_deliberation_validation": "pre-deliberation-validation.json",
    "panel_aggregate": "panel-aggregate.json",
    "panel_summary_markdown": "panel-summary.md",
    "panel_summary_json": "panel-summary.json",
    "review_quality_audit": "review-quality-audit.md",
    "revision_priorities": "revision-priorities.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON must be an object: {path}")
    return value


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def artifact_record(role: str, path: Path, artifact_dir: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing required artifact {role}: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"required artifact is empty {role}: {path}")
    return {
        "role": role,
        "path": path.relative_to(artifact_dir).as_posix(),
        "absolute_path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def validate_calibration_semantics(calibration: dict[str, Any]) -> None:
    try:
        evaluated_on = date.fromisoformat(str(calibration.get("evaluated_on", "")))
    except ValueError as exc:
        raise ValueError("human calibration evaluated_on is not a real ISO date") from exc
    if evaluated_on > date.today():
        raise ValueError("human calibration evaluated_on cannot be in the future")
    metrics = calibration.get("metrics")
    thresholds = calibration.get("thresholds")
    result = calibration.get("result")
    if not isinstance(metrics, dict) or not isinstance(thresholds, dict) or not isinstance(result, dict):
        raise ValueError("human calibration metrics, thresholds, and result are required")
    thresholds_met = all(
        isinstance(metrics.get(name), (int, float))
        and isinstance(threshold, (int, float))
        and metrics[name] >= threshold
        for name, threshold in thresholds.items()
    )
    status = result.get("status")
    if status == "passed" and not thresholds_met:
        raise ValueError("human calibration claims passed but a metric misses its threshold")
    if status == "failed" and thresholds_met:
        raise ValueError("human calibration claims failed although all thresholds are met")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("full-panel",), default="full-panel")
    parser.add_argument("--human-calibration-record")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifact_dir).expanduser().resolve()
    packet_path = Path(args.packet).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not artifact_dir.is_dir():
        print(f"error: artifact directory is missing: {artifact_dir}", file=sys.stderr)
        return 2
    try:
        output.relative_to(artifact_dir)
    except ValueError:
        print("error: artifact manifest output must remain inside --artifact-dir", file=sys.stderr)
        return 2
    try:
        packet = load_json(packet_path)
        records = [
            artifact_record(role, artifact_dir / filename, artifact_dir)
            for role, filename in FULL_PANEL_FILES.items()
        ]
        if args.human_calibration_record:
            calibration_path = Path(args.human_calibration_record).expanduser().resolve()
            calibration = load_json(calibration_path)
            calibration_schema = load_json(
                Path(__file__).resolve().parents[1]
                / "assets"
                / "human-calibration-record.schema.json"
            )
            schema_errors = validate_instance(
                calibration, calibration_schema, path=calibration_path.name
            )
            if schema_errors:
                raise ValueError(
                    "invalid human calibration record: " + "; ".join(schema_errors)
                )
            validate_calibration_semantics(calibration)
            skill_profile = calibration.get("skill_profile")
            expected_protocol_hash = protocol_bundle_sha256(
                Path(__file__).resolve().parents[1]
            )
            if (
                not isinstance(skill_profile, dict)
                or skill_profile.get("protocol_bundle_sha256") != expected_protocol_hash
            ):
                raise ValueError(
                    "human calibration record does not match the current protocol bundle hash"
                )
            records.append(
                artifact_record("human_calibration_record", calibration_path, artifact_dir)
            )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    protected_paths = {packet_path, *(Path(str(record["absolute_path"])) for record in records)}
    if output in protected_paths:
        print(f"error: output manifest aliases a protected input: {output}", file=sys.stderr)
        return 2
    if output.exists():
        for protected in protected_paths:
            try:
                if os.path.samefile(output, protected):
                    print(f"error: output manifest aliases a protected input: {protected}", file=sys.stderr)
                    return 2
            except OSError:
                continue

    payload = {
        "schema_version": "1.0",
        "mode": args.mode,
        "proposal_id": packet.get("proposal_id"),
        "generated_at": utc_now(),
        "artifact_dir": str(artifact_dir),
        "packet_manifest": {
            "absolute_path": str(packet_path),
            "sha256": sha256_file(packet_path),
        },
        "artifacts": sorted(records, key=lambda record: str(record["role"])),
        "notice": "Hash-pinned run inventory; presence and freshness do not establish semantic review correctness.",
    }
    atomic_write(output, payload)
    print(f"wrote {output} ({len(records)} pinned run artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
