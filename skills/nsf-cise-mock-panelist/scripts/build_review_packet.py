#!/usr/bin/env python3
"""Create a local, hash-pinned manifest for an NSF CISE mock review packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


CLASSIFICATIONS = (
    "proposer-owned",
    "organization-authorized",
    "public",
    "third-party-confidential",
    "official-nsf-review-material",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def file_record(raw_path: str, role: str, root: Path) -> dict[str, object]:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"missing {role} file: {path}")
    if not path.is_file():
        raise ValueError(f"{role} input is not a regular file: {path}")
    stat = path.stat()
    return {
        "path": display_path(path, root),
        "absolute_path": str(path),
        "role": role,
        "sha256": sha256_file(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def atomic_json_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Proposal project root")
    parser.add_argument("--output", required=True, help="Manifest JSON path")
    parser.add_argument("--proposal-id", required=True, help="Internal proposal identifier")
    parser.add_argument("--program", default="TBD", help="NSF program and track")
    parser.add_argument("--solicitation-url", default="", help="Exact solicitation URL")
    parser.add_argument(
        "--policy-url", action="append", default=[], help="Additional live policy URL; repeatable"
    )
    parser.add_argument("--policy-verified-on", default="", help="ISO date YYYY-MM-DD")
    parser.add_argument("--proposal", action="append", required=True, help="Proposal file; repeatable")
    parser.add_argument("--supporting", action="append", default=[], help="Supporting file; repeatable")
    parser.add_argument("--authority", action="append", default=[], help="Local authority snapshot; repeatable")
    parser.add_argument("--classification", choices=CLASSIFICATIONS, required=True)
    parser.add_argument("--authorization-note", default="")
    parser.add_argument(
        "--processing-boundary",
        required=True,
        help="Human-readable model/tool processing boundary and authorization statement",
    )
    parser.add_argument(
        "--external-novelty-search-authorized",
        action="store_true",
        help="Record permission for external literature/award queries; never proposal-file upload",
    )
    parser.add_argument(
        "--external-proposal-transfer-authorized",
        action="store_true",
        help="Record explicit authorization to transfer proposal files beyond the named processing boundary",
    )
    parser.add_argument("--policy-max-age-days", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    if args.classification == "official-nsf-review-material":
        print(
            "error: do not process material obtained through service as an official NSF reviewer; "
            "follow NSF confidentiality and approved-tool requirements",
            file=sys.stderr,
        )
        return 2
    if args.classification in {"organization-authorized", "third-party-confidential"} and not args.authorization_note.strip():
        print(f"error: --authorization-note is required for {args.classification}", file=sys.stderr)
        return 2
    if not args.processing_boundary.strip():
        print("error: --processing-boundary must be non-empty", file=sys.stderr)
        return 2
    if args.policy_max_age_days < 0:
        print("error: --policy-max-age-days cannot be negative", file=sys.stderr)
        return 2

    verified_date: date | None = None
    if args.policy_verified_on:
        try:
            verified_date = date.fromisoformat(args.policy_verified_on)
        except ValueError:
            print("error: --policy-verified-on must be an ISO date (YYYY-MM-DD)", file=sys.stderr)
            return 2
        if verified_date > date.today():
            print("error: --policy-verified-on cannot be in the future", file=sys.stderr)
            return 2

    if args.solicitation_url:
        parsed_url = urlparse(args.solicitation_url)
        hostname = (parsed_url.hostname or "").lower()
        if parsed_url.scheme != "https" or not (hostname == "nsf.gov" or hostname.endswith(".nsf.gov")):
            print("error: --solicitation-url must be an official https://*.nsf.gov URL", file=sys.stderr)
            return 2

    try:
        records = [file_record(path, "proposal", root) for path in args.proposal]
        records += [file_record(path, "supporting", root) for path in args.supporting]
        records += [file_record(path, "authority", root) for path in args.authority]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    absolute_paths = [record["absolute_path"] for record in records]
    if len(absolute_paths) != len(set(absolute_paths)):
        print("error: the packet contains duplicate file paths", file=sys.stderr)
        return 2

    output = Path(args.output).expanduser().resolve()
    try:
        output.relative_to(root)
    except ValueError:
        print("error: output manifest must remain inside --root", file=sys.stderr)
        return 2
    for record in records:
        input_path = Path(str(record["absolute_path"]))
        aliases_input = output == input_path
        if output.exists() and input_path.exists():
            try:
                aliases_input = aliases_input or os.path.samefile(output, input_path)
            except OSError:
                pass
        if aliases_input:
            print(f"error: output manifest aliases a pinned input file: {input_path}", file=sys.stderr)
            return 2

    policy_urls = list(dict.fromkeys(([args.solicitation_url] if args.solicitation_url else []) + args.policy_url))
    authority_count = sum(1 for record in records if record["role"] == "authority")
    if args.solicitation_url and verified_date and authority_count:
        age_days = (date.today() - verified_date).days
        policy_status = (
            "authority_pinned" if age_days <= args.policy_max_age_days else "stale_snapshot"
        )
    else:
        age_days = None
        policy_status = "provisional"
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "proposal_id": args.proposal_id,
        "program": args.program,
        "generated_at": utc_now(),
        "root": str(root),
        "processing_authorization": {
            "classification": args.classification,
            "authorization_note": args.authorization_note,
            "processing_boundary": args.processing_boundary,
            "external_novelty_search_authorized": args.external_novelty_search_authorized,
            "external_proposal_transfer_authorized": args.external_proposal_transfer_authorized,
        },
        "policy": {
            "status": policy_status,
            "solicitation_url": args.solicitation_url,
            "urls": policy_urls,
            "verified_on": args.policy_verified_on,
            "age_days_at_manifest_creation": age_days,
            "max_age_days": args.policy_max_age_days,
            "authority_file_count": authority_count,
            "status_meaning": "authority_pinned means a recent local source snapshot is hash-pinned; it does not prove semantic correctness",
        },
        "files": sorted(records, key=lambda item: (str(item["role"]), str(item["path"]))),
        "notice": "Internal mock review packet; not an NSF record or decision.",
    }

    atomic_json_write(output, payload)
    print(f"wrote {output} ({len(records)} pinned files; policy={policy_status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
