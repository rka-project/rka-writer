#!/usr/bin/env python3
"""Validate the holistic academic reviewer without blending native engines.

This standard-library-only wrapper has two deliberately narrow jobs:

1. verify the packaged native review engines against a deterministic manifest;
2. validate a portable session envelope that indexes native artifacts by hash.

The wrapper does not translate, average, or normalize native ratings, scores,
recommendations, dispositions, confidence, or assurance labels. Those remain
under the authority of the selected native engine and its validator. Invoke a
native validator directly from its namespaced engine directory; this wrapper
does not forward arbitrary validator arguments or write review artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parents[1]
SKILLS_ROOT = SKILL_ROOT.parent
ENGINE_MANIFEST_PATH = SKILL_ROOT / "assets" / "engine-manifest.json"

MANIFEST_VERSION = "1.0.0"
SESSION_VERSION = "1.0.0"
HASH_ALGORITHM = "sha256"
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ARTIFACT_ID_PATTERN = re.compile(r"^A-[A-Za-z0-9._-]+$")
OUTPUT_ID_PATTERN = re.compile(r"^O-[A-Za-z0-9._-]+$")


ENGINE_SPECS: dict[str, dict[str, Any]] = {
    "ai-cyber-paper-reviewer": {
        "artifact_kind": "research_paper",
        "root": "ai-cyber-paper-reviewer",
        "validator": "ai-cyber-paper-reviewer/scripts/validate_review.py",
        "native_roles": {
            "paper_venue_profile",
            "paper_review_bundle",
            "paper_referee_report",
            "paper_author_annex",
            "paper_validation_result",
        },
        "authority_profile": "venue_profile",
        "authority_role": "paper_venue_profile",
        "validation_roles": {"paper_validation_result"},
    },
    "nsf-cise-mock-panelist": {
        "artifact_kind": "nsf_cise_proposal",
        "root": "nsf-cise-mock-panelist",
        "validator": "nsf-cise-mock-panelist/scripts/validate_review.py",
        "native_roles": {
            "nsf_cise_packet_manifest",
            "nsf_cise_authority_snapshot",
            "nsf_cise_compliance_screen",
            "nsf_cise_individual_review",
            "nsf_cise_novelty_audit",
            "nsf_cise_methods_audit",
            "nsf_cise_broader_impacts_audit",
            "nsf_cise_presentation_audit",
            "nsf_cise_kill_argument",
            "nsf_cise_kill_adjudication",
            "nsf_cise_issue_ledger",
            "nsf_cise_pre_deliberation_validation",
            "nsf_cise_panel_aggregate",
            "nsf_cise_panel_summary",
            "nsf_cise_review_quality_audit",
            "nsf_cise_run_artifact_manifest",
            "nsf_cise_validation_report",
            "nsf_cise_revision_priorities",
        },
        "authority_profile": "nsf_solicitation_profile",
        "authority_role": "nsf_cise_authority_snapshot",
        "validation_roles": {
            "nsf_cise_pre_deliberation_validation",
            "nsf_cise_validation_report",
        },
    },
}

ARTIFACT_KINDS = {spec["artifact_kind"] for spec in ENGINE_SPECS.values()}
PRIVACY_MODES = {
    "local_only",
    "metadata_only_external_verification",
    "author_authorized_full_external_check",
}
INPUT_ROLES = {
    "primary",
    "supplement",
    "appendix",
    "source",
    "authority",
    "supporting",
    "prior_review",
    "response",
    "other",
}
INSPECTION_STATES = {"complete", "partial", "not_inspected"}
AUTHORITY_STATES = {"verified", "provisional", "unknown"}
VALIDATION_STATES = {"passed", "failed", "not_run"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _is_ignored_engine_path(path: Path, engine_root: Path) -> bool:
    relative = path.relative_to(engine_root)
    return (
        path.name == ".DS_Store"
        or any(part == "__pycache__" for part in relative.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def _safe_relative_path(value: Any, label: str, errors: list[str]) -> PurePosixPath | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a nonempty relative POSIX path")
        return None
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        errors.append(f"{label}: control characters are forbidden")
        return None
    if "\\" in value or value.startswith("~"):
        errors.append(f"{label}: path must use portable relative POSIX syntax")
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        errors.append(f"{label}: absolute paths and traversal are forbidden")
        return None
    if path.as_posix() != value:
        errors.append(f"{label}: path must be normalized")
        return None
    return path


def _resolve_beneath(
    base: Path, relative: PurePosixPath, label: str, errors: list[str]
) -> Path | None:
    try:
        base_resolved = base.resolve()
        unresolved = base_resolved / Path(*relative.parts)
        cursor = base_resolved
        for part in relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                errors.append(f"{label}: symbolic-link path components are forbidden")
                return None
        candidate = unresolved.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"{label}: path cannot be resolved safely: {exc}")
        return None
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        errors.append(f"{label}: resolved path escapes its allowed root")
        return None
    return candidate


def _scan_engine_files(skill_root: Path, engine_id: str) -> list[dict[str, Any]]:
    spec = ENGINE_SPECS[engine_id]
    engine_root = skill_root / spec["root"]
    if engine_root.is_symlink():
        raise ValueError(f"engine directory is a forbidden symbolic link: {spec['root']}")
    if not engine_root.is_dir():
        raise ValueError(f"missing engine directory: {spec['root']}")

    records: list[dict[str, Any]] = []
    for path in engine_root.rglob("*"):
        if path.is_symlink():
            raise ValueError(
                f"engine contains a forbidden symbolic link: {path.relative_to(skill_root)}"
            )
        if not path.is_file() or _is_ignored_engine_path(path, engine_root):
            continue
        records.append(
            {
                "path": path.relative_to(skill_root).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    records.sort(key=lambda record: str(record["path"]))

    validator = skill_root / spec["validator"]
    if not validator.is_file():
        raise ValueError(f"missing native validator: {spec['validator']}")
    return records


def _engine_bundle_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(str(record["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(record["sha256"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(record["size_bytes"]).encode("ascii"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def build_manifest_data(skill_root: Path = SKILLS_ROOT) -> dict[str, Any]:
    engines: list[dict[str, Any]] = []
    for engine_id in sorted(ENGINE_SPECS):
        spec = ENGINE_SPECS[engine_id]
        records = _scan_engine_files(skill_root, engine_id)
        engines.append(
            {
                "id": engine_id,
                "artifact_kind": spec["artifact_kind"],
                "root": spec["root"],
                "validator": spec["validator"],
                "file_count": len(records),
                "engine_bundle_sha256": _engine_bundle_sha256(records),
                "files": records,
            }
        )
    return {
        "manifest_version": MANIFEST_VERSION,
        "hash_algorithm": HASH_ALGORITHM,
        "engines": engines,
    }


def _walk_strings(value: Any, prefix: str = "manifest") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{prefix}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(item, f"{prefix}.{key}")


def _looks_like_absolute_filesystem_path(value: str) -> bool:
    return value.startswith(("/", "~/")) or bool(re.match(r"^[A-Za-z]:[\\/]", value))


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON value must be an object: {path}")
    return value


def verify_engine_manifest(
    skill_root: Path = SKILLS_ROOT, manifest_path: Path | None = None
) -> list[str]:
    errors: list[str] = []
    path = manifest_path or ENGINE_MANIFEST_PATH
    try:
        manifest = load_json_object(path)
    except ValueError as exc:
        return [str(exc)]

    expected_root_keys = {"manifest_version", "hash_algorithm", "engines"}
    if set(manifest) != expected_root_keys:
        errors.append("manifest: unexpected or missing top-level fields")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append("manifest.manifest_version: unsupported version")
    if manifest.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append("manifest.hash_algorithm: must be sha256")
    for label, value in _walk_strings(manifest):
        if _looks_like_absolute_filesystem_path(value):
            errors.append(f"{label}: personal or absolute filesystem paths are forbidden")

    engine_values = manifest.get("engines")
    if not isinstance(engine_values, list):
        errors.append("manifest.engines: expected an array")
        return errors

    engine_ids = [item.get("id") for item in engine_values if isinstance(item, dict)]
    if engine_ids != sorted(ENGINE_SPECS):
        errors.append("manifest.engines: must contain exactly the known engines in canonical order")

    recorded_by_id: dict[str, dict[str, Any]] = {}
    for index, engine in enumerate(engine_values):
        label = f"manifest.engines[{index}]"
        if not isinstance(engine, dict):
            errors.append(f"{label}: expected an object")
            continue
        expected_engine_keys = {
            "id",
            "artifact_kind",
            "root",
            "validator",
            "file_count",
            "engine_bundle_sha256",
            "files",
        }
        if set(engine) != expected_engine_keys:
            errors.append(f"{label}: unexpected or missing fields")
        engine_id = engine.get("id")
        if not isinstance(engine_id, str) or engine_id not in ENGINE_SPECS:
            errors.append(f"{label}.id: unknown engine")
            continue
        if engine_id in recorded_by_id:
            errors.append(f"{label}.id: duplicate engine")
            continue
        recorded_by_id[engine_id] = engine
        spec = ENGINE_SPECS[engine_id]
        if engine.get("artifact_kind") != spec["artifact_kind"]:
            errors.append(f"{label}.artifact_kind: does not match the native engine")
        if engine.get("root") != spec["root"]:
            errors.append(f"{label}.root: does not match the native engine")
        if engine.get("validator") != spec["validator"]:
            errors.append(f"{label}.validator: does not match the native engine")

        for field in ("root", "validator"):
            relative = _safe_relative_path(engine.get(field), f"{label}.{field}", errors)
            if relative is not None:
                _resolve_beneath(skill_root, relative, f"{label}.{field}", errors)

        files = engine.get("files")
        if not isinstance(files, list):
            errors.append(f"{label}.files: expected an array")
            continue
        if (
            not isinstance(engine.get("file_count"), int)
            or isinstance(engine.get("file_count"), bool)
            or engine.get("file_count") != len(files)
        ):
            errors.append(f"{label}.file_count: does not match files")
        paths: list[str] = []
        for file_index, record in enumerate(files):
            file_label = f"{label}.files[{file_index}]"
            if not isinstance(record, dict):
                errors.append(f"{file_label}: expected an object")
                continue
            if set(record) != {"path", "sha256", "size_bytes"}:
                errors.append(f"{file_label}: unexpected or missing fields")
            relative = _safe_relative_path(record.get("path"), f"{file_label}.path", errors)
            if relative is not None:
                resolved = _resolve_beneath(skill_root, relative, f"{file_label}.path", errors)
                expected_prefix = PurePosixPath(str(spec["root"]))
                try:
                    relative.relative_to(expected_prefix)
                except ValueError:
                    errors.append(f"{file_label}.path: file is outside the declared engine root")
                if resolved is not None and resolved.is_symlink():
                    errors.append(f"{file_label}.path: symbolic links are forbidden")
            if isinstance(record.get("path"), str):
                paths.append(record["path"])
            if not isinstance(record.get("sha256"), str) or not SHA256_PATTERN.fullmatch(
                str(record.get("sha256", ""))
            ):
                errors.append(f"{file_label}.sha256: invalid SHA-256")
            if (
                not isinstance(record.get("size_bytes"), int)
                or isinstance(record.get("size_bytes"), bool)
                or record.get("size_bytes", -1) < 0
            ):
                errors.append(f"{file_label}.size_bytes: expected a nonnegative integer")
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            errors.append(f"{label}.files: paths must be unique and canonically sorted")
        if engine.get("validator") not in set(paths):
            errors.append(f"{label}.validator: native validator is not covered by the manifest")
        try:
            computed_bundle_hash = _engine_bundle_sha256(
                [record for record in files if isinstance(record, dict)]
            )
        except (AttributeError, KeyError, TypeError, UnicodeError, ValueError) as exc:
            errors.append(
                f"{label}.engine_bundle_sha256: cannot be recomputed from malformed file records: {exc}"
            )
        else:
            if engine.get("engine_bundle_sha256") != computed_bundle_hash:
                errors.append(f"{label}.engine_bundle_sha256: inconsistent with file records")

    try:
        current = build_manifest_data(skill_root)
    except (OSError, ValueError) as exc:
        errors.append(f"engine scan failed: {exc}")
        return errors

    current_by_id = {engine["id"]: engine for engine in current["engines"]}
    for engine_id in sorted(ENGINE_SPECS):
        recorded = recorded_by_id.get(engine_id)
        if recorded is None:
            continue
        current_engine = current_by_id[engine_id]
        recorded_files = {
            item.get("path"): item
            for item in recorded.get("files", [])
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        current_files = {item["path"]: item for item in current_engine["files"]}
        for missing in sorted(set(recorded_files) - set(current_files)):
            errors.append(f"{engine_id}: manifested file is missing: {missing}")
        for untracked in sorted(set(current_files) - set(recorded_files)):
            errors.append(f"{engine_id}: engine file is not manifested: {untracked}")
        for common in sorted(set(recorded_files) & set(current_files)):
            if recorded_files[common] != current_files[common]:
                errors.append(f"{engine_id}: engine file failed integrity verification: {common}")
        if recorded.get("engine_bundle_sha256") != current_engine["engine_bundle_sha256"]:
            errors.append(f"{engine_id}: engine bundle digest does not match current files")
    return errors


def _exact_keys(
    value: Mapping[str, Any], required: set[str], optional: set[str], label: str, errors: list[str]
) -> None:
    missing = required - set(value)
    extra = set(value) - required - optional
    if missing:
        errors.append(f"{label}: missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{label}: unexpected fields: {', '.join(sorted(extra))}")


def _nonempty_string(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: expected a nonempty string")
        return False
    return True


def _valid_timestamp(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected an RFC 3339 date-time")
        return False
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        errors.append(f"{label}: invalid RFC 3339 date-time")
        return False
    if parsed.tzinfo is None:
        errors.append(f"{label}: date-time must include a timezone")
        return False
    return True


def _verify_indexed_file(
    base: Path, record: Mapping[str, Any], label: str, errors: list[str]
) -> tuple[str, tuple[int, int]] | None:
    relative = _safe_relative_path(record.get("path"), f"{label}.path", errors)
    if relative is None:
        return None
    resolved = _resolve_beneath(base, relative, f"{label}.path", errors)
    if resolved is None:
        return None
    try:
        if not resolved.is_file():
            errors.append(f"{label}.path: indexed file does not exist")
            return None
        stat_result = resolved.stat()
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"{label}.path: indexed file cannot be inspected safely: {exc}")
        return None
    expected_hash = record.get("sha256")
    if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
        errors.append(f"{label}.sha256: invalid SHA-256")
    else:
        try:
            actual_hash = sha256_file(resolved)
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"{label}.path: indexed file cannot be hashed safely: {exc}")
            return None
        if actual_hash != expected_hash:
            errors.append(f"{label}.sha256: indexed file hash is stale")
    return relative.as_posix(), (int(stat_result.st_dev), int(stat_result.st_ino))


def validate_session_data(
    session: Mapping[str, Any],
    session_path: Path,
    skill_root: Path = SKILLS_ROOT,
    manifest_path: Path | None = None,
) -> list[str]:
    errors = verify_engine_manifest(skill_root, manifest_path)
    if errors:
        return [f"engine manifest: {message}" for message in errors]

    required = {
        "schema_version",
        "session_id",
        "created_at",
        "artifact_kind",
        "engine_id",
        "privacy_mode",
        "authority",
        "engine_manifest_sha256",
        "input_artifacts",
        "native_outputs",
        "native_validation",
        "limitations",
    }
    _exact_keys(session, required, set(), "session", errors)
    if session.get("schema_version") != SESSION_VERSION:
        errors.append("session.schema_version: unsupported version")
    session_id = session.get("session_id")
    if not isinstance(session_id, str) or not SESSION_ID_PATTERN.fullmatch(session_id):
        errors.append("session.session_id: invalid identifier")
    _valid_timestamp(session.get("created_at"), "session.created_at", errors)

    artifact_kind = session.get("artifact_kind")
    if artifact_kind not in ARTIFACT_KINDS:
        errors.append("session.artifact_kind: unsupported artifact kind")
    engine_id = session.get("engine_id")
    if engine_id not in ENGINE_SPECS:
        errors.append("session.engine_id: unsupported native engine")
        spec: Mapping[str, Any] | None = None
    else:
        spec = ENGINE_SPECS[str(engine_id)]
        if artifact_kind != spec["artifact_kind"]:
            errors.append("session: artifact_kind and engine_id do not match")
    if session.get("privacy_mode") not in PRIVACY_MODES:
        errors.append("session.privacy_mode: unsupported privacy mode")

    actual_manifest_path = manifest_path or ENGINE_MANIFEST_PATH
    expected_manifest_hash = sha256_file(actual_manifest_path)
    if session.get("engine_manifest_sha256") != expected_manifest_hash:
        errors.append("session.engine_manifest_sha256: does not match the packaged manifest")

    authority = session.get("authority")
    if not isinstance(authority, dict):
        errors.append("session.authority: expected an object")
        authority = {}
    else:
        _exact_keys(
            authority,
            {"profile", "status", "snapshot_output_id"},
            set(),
            "session.authority",
            errors,
        )
        if authority.get("status") not in AUTHORITY_STATES:
            errors.append("session.authority.status: unsupported authority status")
        snapshot_id = authority.get("snapshot_output_id")
        if snapshot_id is not None and (
            not isinstance(snapshot_id, str) or not OUTPUT_ID_PATTERN.fullmatch(snapshot_id)
        ):
            errors.append("session.authority.snapshot_output_id: invalid output identifier")
        if authority.get("status") == "verified" and not isinstance(snapshot_id, str):
            errors.append(
                "session.authority.snapshot_output_id: verified authority requires a linked snapshot"
            )
        if spec is not None and authority.get("profile") != spec["authority_profile"]:
            errors.append("session.authority.profile: does not match the selected engine")

    base = session_path.resolve().parent
    input_values = session.get("input_artifacts")
    input_ids: set[str] = set()
    input_paths: set[str] = set()
    input_file_ids: set[tuple[int, int]] = set()
    if not isinstance(input_values, list) or not input_values:
        errors.append("session.input_artifacts: expected a nonempty array")
        input_values = []
    for index, record in enumerate(input_values):
        label = f"session.input_artifacts[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: expected an object")
            continue
        _exact_keys(
            record,
            {"artifact_id", "role", "path", "sha256", "media_type", "inspection_status"},
            set(),
            label,
            errors,
        )
        artifact_id = record.get("artifact_id")
        if not isinstance(artifact_id, str) or not ARTIFACT_ID_PATTERN.fullmatch(artifact_id):
            errors.append(f"{label}.artifact_id: invalid artifact identifier")
        elif artifact_id in input_ids:
            errors.append(f"{label}.artifact_id: duplicate identifier")
        else:
            input_ids.add(artifact_id)
        if record.get("role") not in INPUT_ROLES:
            errors.append(f"{label}.role: unsupported input role")
        if record.get("inspection_status") not in INSPECTION_STATES:
            errors.append(f"{label}.inspection_status: unsupported inspection status")
        _nonempty_string(record.get("media_type"), f"{label}.media_type", errors)
        verified_file = _verify_indexed_file(base, record, label, errors)
        if verified_file is not None:
            relative, file_id = verified_file
            if relative in input_paths:
                errors.append(f"{label}.path: duplicate indexed input path")
            if file_id in input_file_ids:
                errors.append(f"{label}.path: input aliases another indexed input file")
            input_paths.add(relative)
            input_file_ids.add(file_id)

    output_values = session.get("native_outputs")
    output_ids: set[str] = set()
    output_paths: set[str] = set()
    output_file_ids: set[tuple[int, int]] = set()
    outputs_by_id: dict[str, Mapping[str, Any]] = {}
    if not isinstance(output_values, list) or not output_values:
        errors.append("session.native_outputs: expected a nonempty array")
        output_values = []
    for index, record in enumerate(output_values):
        label = f"session.native_outputs[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: expected an object")
            continue
        _exact_keys(
            record,
            {"output_id", "native_role", "path", "sha256", "media_type"},
            set(),
            label,
            errors,
        )
        output_id = record.get("output_id")
        if not isinstance(output_id, str) or not OUTPUT_ID_PATTERN.fullmatch(output_id):
            errors.append(f"{label}.output_id: invalid output identifier")
        elif output_id in output_ids:
            errors.append(f"{label}.output_id: duplicate identifier")
        else:
            output_ids.add(output_id)
            outputs_by_id[output_id] = record
        if spec is not None and record.get("native_role") not in spec["native_roles"]:
            errors.append(f"{label}.native_role: role belongs to a different or unknown engine")
        _nonempty_string(record.get("media_type"), f"{label}.media_type", errors)
        verified_file = _verify_indexed_file(base, record, label, errors)
        if verified_file is not None:
            relative, file_id = verified_file
            if relative in output_paths:
                errors.append(f"{label}.path: duplicate indexed output path")
            if relative in input_paths:
                errors.append(f"{label}.path: native output must not overwrite an input artifact")
            if file_id in input_file_ids:
                errors.append(f"{label}.path: native output aliases an input artifact")
            if file_id in output_file_ids:
                errors.append(f"{label}.path: output aliases another indexed output file")
            output_paths.add(relative)
            output_file_ids.add(file_id)

    snapshot_id = authority.get("snapshot_output_id") if isinstance(authority, dict) else None
    if isinstance(snapshot_id, str):
        snapshot = outputs_by_id.get(snapshot_id)
        if snapshot is None:
            errors.append("session.authority.snapshot_output_id: unknown native output")
        elif spec is not None and snapshot.get("native_role") != spec["authority_role"]:
            errors.append("session.authority.snapshot_output_id: wrong native output role")

    native_validation = session.get("native_validation")
    if not isinstance(native_validation, dict):
        errors.append("session.native_validation: expected an object")
        native_validation = {}
    else:
        _exact_keys(
            native_validation,
            {"status", "validator", "validator_exit_code", "validated_at", "report_output_id"},
            set(),
            "session.native_validation",
            errors,
        )
        status = native_validation.get("status")
        if status not in VALIDATION_STATES:
            errors.append("session.native_validation.status: unsupported validation status")
        if spec is not None and native_validation.get("validator") != spec["validator"]:
            errors.append("session.native_validation.validator: wrong native validator")
        validator_relative = _safe_relative_path(
            native_validation.get("validator"), "session.native_validation.validator", errors
        )
        if validator_relative is not None:
            _resolve_beneath(skill_root, validator_relative, "session.native_validation.validator", errors)
        exit_code = native_validation.get("validator_exit_code")
        validated_at = native_validation.get("validated_at")
        report_output_id = native_validation.get("report_output_id")
        if report_output_id is not None and (
            not isinstance(report_output_id, str)
            or not OUTPUT_ID_PATTERN.fullmatch(report_output_id)
        ):
            errors.append("session.native_validation.report_output_id: invalid output identifier")
        if status == "not_run":
            if exit_code is not None or validated_at is not None or report_output_id is not None:
                errors.append(
                    "session.native_validation: not_run must not claim an exit code, time, or report"
                )
        elif status in {"passed", "failed"}:
            if not isinstance(exit_code, int) or isinstance(exit_code, bool):
                errors.append("session.native_validation.validator_exit_code: expected an integer")
            elif status == "passed" and exit_code != 0:
                errors.append("session.native_validation: passed requires exit code 0")
            elif status == "failed" and exit_code == 0:
                errors.append("session.native_validation: failed requires a nonzero exit code")
            _valid_timestamp(validated_at, "session.native_validation.validated_at", errors)
            if not isinstance(report_output_id, str):
                errors.append(
                    "session.native_validation.report_output_id: completed validation requires a linked report"
                )
        if isinstance(report_output_id, str):
            report = outputs_by_id.get(report_output_id)
            if report is None:
                errors.append("session.native_validation.report_output_id: unknown native output")
            elif spec is not None and report.get("native_role") not in spec["validation_roles"]:
                errors.append("session.native_validation.report_output_id: wrong native output role")

    limitations = session.get("limitations")
    if not isinstance(limitations, list):
        errors.append("session.limitations: expected an array")
    else:
        for index, limitation in enumerate(limitations):
            _nonempty_string(limitation, f"session.limitations[{index}]", errors)
    return errors


def validate_session_file(
    session_path: Path,
    skill_root: Path = SKILLS_ROOT,
    manifest_path: Path | None = None,
) -> list[str]:
    try:
        session = load_json_object(session_path)
    except ValueError as exc:
        return [str(exc)]
    return validate_session_data(session, session_path, skill_root, manifest_path)


def manifest_engine_rows(manifest_path: Path = ENGINE_MANIFEST_PATH) -> list[dict[str, Any]]:
    manifest = load_json_object(manifest_path)
    values = manifest.get("engines")
    if not isinstance(values, list):
        raise ValueError("engine manifest does not contain an engines array")
    return [
        {
            "id": value["id"],
            "artifact_kind": value["artifact_kind"],
            "validator": value["validator"],
            "engine_bundle_sha256": value["engine_bundle_sha256"],
        }
        for value in values
        if isinstance(value, dict)
    ]


def _print_result(ok: bool, errors: Sequence[str], json_mode: bool, **extra: Any) -> None:
    if json_mode:
        payload: dict[str, Any] = {"valid": ok, "errors": list(errors)}
        payload.update(extra)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if ok:
        print(extra.get("message", "valid"))
    else:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-engines", help="list packaged native engines")
    list_parser.add_argument("--json", action="store_true")

    verify_parser = subparsers.add_parser(
        "verify-engines", help="verify native engine files against the packaged manifest"
    )
    verify_parser.add_argument("--json", action="store_true")

    session_parser = subparsers.add_parser(
        "validate-session", help="validate a common session envelope and indexed files"
    )
    session_parser.add_argument("session", type=Path)
    session_parser.add_argument("--json", action="store_true")

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "verify-engines":
        errors = verify_engine_manifest()
        _print_result(
            not errors,
            errors,
            args.json,
            message=(
                "engine manifest and native engine files are valid"
                if not errors
                else "engine manifest validation failed"
            ),
            engine_count=len(ENGINE_SPECS),
        )
        return 0 if not errors else 1

    if args.command == "list-engines":
        errors = verify_engine_manifest()
        if errors:
            _print_result(False, errors, args.json)
            return 1
        rows = manifest_engine_rows()
        if args.json:
            print(json.dumps({"engines": rows}, indent=2, sort_keys=True))
        else:
            for row in rows:
                print(f"{row['id']}\t{row['artifact_kind']}\t{row['validator']}")
        return 0

    if args.command == "validate-session":
        errors = validate_session_file(args.session)
        _print_result(
            not errors,
            errors,
            args.json,
            message=(
                "academic session envelope and indexed files are valid"
                if not errors
                else "academic session validation failed"
            ),
            session=str(args.session),
        )
        return 0 if not errors else 1

    print("error: unsupported command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
