#!/usr/bin/env python3
"""Compute a canonical digest for behavior-bearing mock-panelist files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROTOCOL_FILES = ("SKILL.md",)
PROTOCOL_TREES = {
    "agents": {".yaml", ".yml"},
    "assets": {".json"},
    "references": {".md"},
    "scripts": {".py"},
}


def protocol_records(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    paths: list[Path] = []
    for relative in PROTOCOL_FILES:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing protocol file: {path}")
        paths.append(path)
    for directory, suffixes in PROTOCOL_TREES.items():
        tree = root / directory
        if not tree.is_dir():
            raise ValueError(f"missing protocol directory: {tree}")
        paths.extend(
            path
            for path in tree.rglob("*")
            if path.is_file()
            and path.suffix in suffixes
            and "__pycache__" not in path.parts
            and not path.name.startswith(".")
        )

    records: list[dict[str, Any]] = []
    for path in sorted(set(paths), key=lambda item: item.relative_to(root).as_posix()):
        payload = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
            }
        )
    return records


def protocol_bundle_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for record in protocol_records(root):
        digest.update(str(record["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(record["sha256"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(record["size_bytes"]).encode("ascii"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Skill root; defaults to the parent of this script directory.",
    )
    parser.add_argument("--json", action="store_true", help="Include the file manifest.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    try:
        digest = protocol_bundle_sha256(root)
        records = protocol_records(root)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "protocol_bundle_sha256": digest,
                    "files": records,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
