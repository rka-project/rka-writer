"""Strict, staging-only importer for RKA Core legacy Writer bundles.

This module is intentionally independent of RKA Core.  It accepts the frozen
``rka-legacy-writer-export/v1`` file contract, materializes canonical JSONL
records in a content-addressed directory, and verifies that the staged records
reconstruct the source payload exactly.  It never changes Writer authority.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


CONTRACT_PATH = Path(__file__).with_name("contracts") / "rka-legacy-writer-export-v1.json"
EQUIVALENCE_CONTRACT = "rka-writer-staging-equivalence/v1"
COMPLETE_MARKER = "COMPLETE"
PROJECT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARCHIVE_MEMBERS = 64
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024

_BINDING_TABLES = (
    "manuscript_claim_evidence",
    "manuscript_claim_units",
    "manuscript_planning_evidence_bindings",
    "manuscript_unit_citations",
    "manuscript_unit_evidence",
)
_RATIFICATION_TABLES = ("manuscript_claim_ratifications",)
_SOURCE_REFERENCE_TABLES = (
    "manuscript_reference_members",
    "manuscript_source_events",
    "manuscript_source_proposals",
    "reference_validation_attestations",
)
_LOGICAL_INTERNAL_TARGETS = {
    "manuscript": "manuscripts",
    "manuscript_claim": "manuscript_claims",
    "manuscript_claim_ratification": "manuscript_claim_ratifications",
    "manuscript_unit": "manuscript_units",
    "semantic_patch_proposal": "semantic_patch_proposals",
    "manuscript_checkpoint": "manuscript_checkpoints",
    "manuscript_claim_verification": "manuscript_claim_verification_attestations",
    "manuscript_reference": "manuscript_reference_members",
    "reference_validation": "reference_validation_attestations",
}
_INTERNAL_WRITER_ENTITY_TYPES = frozenset(_LOGICAL_INTERNAL_TARGETS)
_CORE_ENTITY_TABLES = {
    "project": "projects",
    "journal": "journal",
    "literature": "literature",
    "decision": "decisions",
    "claim": "claims",
    "claim_scope": "claim_scope_versions",
    "cluster": "evidence_clusters",
    "interpretation_candidate": "interpretation_candidates",
    "interpretation_hint": "interpretation_candidate_hints",
    "interpretation_review": "interpretation_review_events",
    "interpretation_promotion": "interpretation_promotions",
    "experiment": "experiments",
    "experiment_plan_version": "experiment_plan_versions",
    "experiment_run": "experiment_runs",
    "experiment_observation": "experiment_observations",
    "evidence_locator": "evidence_locators",
    "artifact": "artifacts",
    "mission": "missions",
    "job": "jobs",
    "checkpoint": "checkpoints",
    "figure": "figures",
    "topic": "topics",
    "review": "review_queue",
    "event": "events",
    "link": "entity_links",
    "claim_edge": "claim_edges",
    "decision_option": "decision_options",
    "reference_validation": "reference_validation_attestations",
}
_DIRECT_CORE_REFERENCES = (
    ("manuscripts", "legacy_journal_id", "journal"),
    ("manuscript_migration_issues", "legacy_journal_id", "journal"),
    ("manuscript_checkpoints", "decision_id", "decision"),
    ("manuscript_claim_ratifications", "decision_id", "decision"),
    ("manuscript_claim_evidence", "evidence_claim_id", "claim"),
    ("manuscript_unit_evidence", "evidence_claim_id", "claim"),
    ("manuscript_reference_members", "literature_id", "literature"),
    ("reference_validation_attestations", "legacy_journal_id", "journal"),
    ("reference_validation_attestations", "validation_job_id", "job"),
    ("reference_validation_attestations", "literature_id", "literature"),
    ("manuscript_evaluation_events", "mission_id", "mission"),
    ("manuscript_planning_promotion_events", "decision_id", "decision"),
)
_ENTITY_TYPES_BY_ID_PREFIX = {
    "jrn": "journal",
    "lit": "literature",
    "dec": "decision",
    "clm": "claim",
    "csc": "claim_scope",
    "ecl": "cluster",
    "icd": "interpretation_candidate",
    "ich": "interpretation_hint",
    "icv": "interpretation_review",
    "ipm": "interpretation_promotion",
    "exp": "experiment",
    "epv": "experiment_plan_version",
    "run": "experiment_run",
    "obs": "experiment_observation",
    "elc": "evidence_locator",
    "art": "artifact",
    "mis": "mission",
    "prj": "project",
    "chk": "checkpoint",
    "fig": "figure",
    "top": "topic",
    "rev": "review",
    "evt": "event",
    "lnk": "link",
    "ced": "claim_edge",
    "dop": "decision_option",
    "rvd": "reference_validation",
    "man": "manuscript",
    "mcl": "manuscript_claim",
    "mra": "manuscript_claim_ratification",
    "mun": "manuscript_unit",
    "mck": "manuscript_checkpoint",
    "mva": "manuscript_claim_verification",
    "mrf": "manuscript_reference",
    "spp": "semantic_patch_proposal",
}


class StagingError(RuntimeError):
    """The bundle or staged representation violates the frozen v1 contract."""


@dataclass(frozen=True)
class _InspectedBundle:
    path: Path
    file_sha256: str
    contract: dict[str, Any]
    manifest: dict[str, Any]
    rows: dict[str, list[dict[str, Any]]]
    table_payloads: dict[str, bytes]
    internal_reference_count: int

    @property
    def project_id(self) -> str:
        return str(self.manifest["source"]["project_id"])

    @property
    def semantic_root_sha256(self) -> str:
        return str(self.manifest["semantic_root_sha256"])


def inspect_bundle(bundle: str | Path) -> dict[str, Any]:
    """Validate a bundle without writing staging state."""

    inspected = _inspect_bundle(Path(bundle))
    return {
        "authority_switched": False,
        "contract": inspected.manifest["contract"],
        "core_reference_count": len(inspected.manifest["core_references"]),
        "file_sha256": inspected.file_sha256,
        "internal_reference_count": inspected.internal_reference_count,
        "project_id": inspected.project_id,
        "row_count": inspected.manifest["row_count"],
        "schema_fingerprint": inspected.manifest["schema_fingerprint"],
        "semantic_root_sha256": inspected.semantic_root_sha256,
        "status": "valid",
        "table_count": inspected.manifest["table_count"],
        "tables_sha256": inspected.manifest["tables_sha256"],
    }


def stage_bundle(bundle: str | Path, staging_root: str | Path) -> dict[str, Any]:
    """Atomically materialize and verify one content-addressed staging tree."""

    inspected = _inspect_bundle(Path(bundle))
    root = _prepare_staging_root(Path(staging_root))
    project_root = root / inspected.project_id
    project_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    _reject_symlink(project_root, "project staging directory")
    destination = project_root / inspected.semantic_root_sha256

    if destination.exists():
        return verify_stage(bundle, staging_root)

    temporary = Path(tempfile.mkdtemp(prefix=f".{inspected.semantic_root_sha256}.", dir=project_root))
    os.chmod(temporary, 0o700)
    try:
        records_root = temporary / "records"
        records_root.mkdir(mode=0o700)
        for table in _contract_tables(inspected.contract):
            payload = b"".join(_canonical_json(row) + b"\n" for row in inspected.rows[table])
            _write_file(records_root / f"{table}.jsonl", payload)

        source_path = temporary / "source-bundle.zip"
        _copy_file(inspected.path, source_path)

        stage_manifest = _stage_manifest(inspected)
        _write_json(temporary / "stage-manifest.json", stage_manifest)
        report = _equivalence_report(inspected, inspected.rows)
        report_payload = _canonical_json(report) + b"\n"
        _write_file(temporary / "equivalence-report.json", report_payload)
        _write_file(
            temporary / COMPLETE_MARKER,
            (_sha256(report_payload) + "\n").encode("ascii"),
        )
        _fsync_directory(records_root)
        _fsync_directory(temporary)

        # Verify the independent staged representation, including reconstruction,
        # before publishing it under the content-addressed final name.
        _verify_staged_directory(inspected.path, temporary)
        try:
            os.rename(temporary, destination)
        except OSError as exc:
            if exc.errno not in {errno.EEXIST, errno.ENOTEMPTY}:
                raise
            # A concurrent identical import won the race.  Its bytes still have
            # to pass the same verification gate before it is accepted.  macOS
            # commonly reports ENOTEMPTY for this directory-rename race, while
            # Linux commonly reports EEXIST.
            shutil.rmtree(temporary)
            return verify_stage(bundle, staging_root)
        _fsync_directory(project_root)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

    return verify_stage(bundle, staging_root)


def verify_stage(bundle: str | Path, staging_root: str | Path) -> dict[str, Any]:
    """Reconstruct a staged bundle from JSONL and compare it with its source."""

    inspected = _inspect_bundle(Path(bundle))
    root = _prepare_staging_root(Path(staging_root), create=False)
    destination = root / inspected.project_id / inspected.semantic_root_sha256
    return _verify_staged_directory(inspected.path, destination)


def _inspect_bundle(path: Path) -> _InspectedBundle:
    contract = _load_contract()
    path = path.expanduser()
    _reject_symlink(path, "bundle")
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise StagingError(f"Bundle not found: {path}") from exc
    if not resolved.is_file():
        raise StagingError(f"Bundle is not a regular file: {resolved}")

    try:
        with zipfile.ZipFile(resolved) as archive:
            infos = archive.infolist()
            _validate_archive_members(infos)
            info_by_name = {info.filename: info for info in infos}
            manifest_info = info_by_name.get("manifest.json")
            if manifest_info is None:
                raise StagingError("Bundle is missing manifest.json")
            if manifest_info.file_size > MAX_MANIFEST_BYTES:
                raise StagingError("manifest.json exceeds the staging size limit")
            manifest = _load_json_bytes(archive.read(manifest_info), "manifest.json")
            if not isinstance(manifest, dict):
                raise StagingError("manifest.json must contain a JSON object")
            _validate_manifest_shape(manifest, contract)

            table_names = _contract_tables(contract)
            expected_members = {"manifest.json"}
            for table in table_names:
                expected_members.add(str(manifest["tables"][table]["path"]))
            actual_members = set(info_by_name)
            if actual_members != expected_members:
                missing = sorted(expected_members - actual_members)
                extra = sorted(actual_members - expected_members)
                raise StagingError(
                    "Bundle member inventory mismatch"
                    + (f"; missing={missing}" if missing else "")
                    + (f"; extra={extra}" if extra else "")
                )

            rows: dict[str, list[dict[str, Any]]] = {}
            table_payloads: dict[str, bytes] = {}
            for table in table_names:
                descriptor = manifest["tables"][table]
                member = info_by_name[descriptor["path"]]
                payload = archive.read(member)
                if _sha256(payload) != descriptor["sha256"]:
                    raise StagingError(f"Table checksum mismatch: {table}")
                parsed = _load_json_bytes(payload, descriptor["path"])
                if not isinstance(parsed, list):
                    raise StagingError(f"Table payload must be an array: {table}")
                if payload != _canonical_json(parsed):
                    raise StagingError(f"Table payload is not canonical JSON: {table}")
                normalized_rows = _validate_table_rows(
                    table,
                    parsed,
                    descriptor,
                    str(manifest["source"]["project_id"]),
                    contract,
                )
                rows[table] = normalized_rows
                table_payloads[table] = payload
                primary_key = descriptor["primary_key"]
                primary_key_payload = _canonical_json(
                    [
                        {column: row[column] for column in primary_key}
                        for row in normalized_rows
                    ]
                )
                if _sha256(primary_key_payload) != descriptor["primary_key_sha256"]:
                    raise StagingError(f"Primary-key checksum mismatch: {table}")

            _validate_core_reference_sources(manifest, rows)
            internal_reference_count = _validate_internal_references(
                rows, manifest["tables"], table_names
            )
            _validate_aggregates(manifest, contract)
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        if isinstance(exc, StagingError):
            raise
        raise StagingError(f"Cannot read legacy Writer bundle: {exc}") from exc

    return _InspectedBundle(
        path=resolved,
        file_sha256=_sha256_file(resolved),
        contract=contract,
        manifest=manifest,
        rows=rows,
        table_payloads=table_payloads,
        internal_reference_count=internal_reference_count,
    )


def _load_contract() -> dict[str, Any]:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StagingError(f"Cannot load Writer bundle contract: {exc}") from exc
    if not isinstance(contract, dict):
        raise StagingError("Writer bundle contract must be a JSON object")
    tables = contract.get("tables")
    if not isinstance(tables, list) or not tables or any(
        not isinstance(table, str) or not table for table in tables
    ):
        raise StagingError("Writer bundle contract has an invalid table inventory")
    if len(tables) != len(set(tables)):
        raise StagingError("Writer bundle contract contains duplicate tables")
    return contract


def _contract_tables(contract: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(table) for table in contract["tables"])


def _validate_archive_members(infos: Sequence[zipfile.ZipInfo]) -> None:
    if not infos:
        raise StagingError("Bundle archive is empty")
    if len(infos) > MAX_ARCHIVE_MEMBERS:
        raise StagingError("Bundle contains too many archive members")
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        raise StagingError("Bundle contains duplicate archive members")
    total_size = 0
    for info in infos:
        path = PurePosixPath(info.filename)
        mode = info.external_attr >> 16
        if (
            info.is_dir()
            or not info.filename
            or "\\" in info.filename
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or stat.S_ISLNK(mode)
        ):
            raise StagingError(f"Unsafe archive member: {info.filename!r}")
        if info.flag_bits & 0x1:
            raise StagingError(f"Encrypted archive members are unsupported: {info.filename}")
        if info.file_size > MAX_MEMBER_BYTES:
            raise StagingError(f"Archive member exceeds size limit: {info.filename}")
        total_size += info.file_size
        if total_size > MAX_TOTAL_BYTES:
            raise StagingError("Bundle exceeds the total uncompressed size limit")


def _validate_manifest_shape(manifest: dict[str, Any], contract: dict[str, Any]) -> None:
    required = contract.get("required_manifest_fields")
    if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
        raise StagingError("Writer contract has invalid required_manifest_fields")
    missing = sorted(set(required) - set(manifest))
    if missing:
        raise StagingError(f"Manifest is missing required fields: {missing}")
    allowed = set(required) | {
        "exported_at",
        "nonportable_fields",
        "sensitive_fields",
    }
    optional = contract.get("optional_manifest_fields", [])
    if not isinstance(optional, list) or any(not isinstance(item, str) for item in optional):
        raise StagingError("Writer contract has invalid optional_manifest_fields")
    allowed.update(optional)
    unknown = sorted(set(manifest) - allowed)
    if unknown:
        raise StagingError(f"Manifest contains unsupported fields: {unknown}")

    if manifest.get("contract") != contract.get("contract"):
        raise StagingError(f"Unsupported bundle contract: {manifest.get('contract')!r}")
    if manifest.get("format_version") != contract.get("format_version"):
        raise StagingError(f"Unsupported bundle format version: {manifest.get('format_version')!r}")
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise StagingError("Manifest source must be an object")
    project_id = source.get("project_id")
    if not isinstance(project_id, str) or not PROJECT_ID_RE.fullmatch(project_id):
        raise StagingError("Manifest source.project_id is invalid")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or authority.get("authority_switched") is not False:
        raise StagingError("Bundle must attest authority_switched=false")

    table_names = _contract_tables(contract)
    if manifest.get("required_tables") != list(table_names):
        raise StagingError("Manifest required_tables does not match the frozen v1 inventory")
    tables = manifest.get("tables")
    if not isinstance(tables, dict) or set(tables) != set(table_names):
        raise StagingError("Manifest tables does not match the frozen v1 inventory")
    if manifest.get("table_count") != len(table_names):
        raise StagingError("Manifest table_count is invalid")
    if isinstance(manifest.get("row_count"), bool) or not isinstance(
        manifest.get("row_count"), int
    ) or manifest["row_count"] < 0:
        raise StagingError("Manifest row_count is invalid")

    required_descriptor = contract.get("required_table_descriptor_fields")
    if not isinstance(required_descriptor, list) or any(
        not isinstance(item, str) for item in required_descriptor
    ):
        raise StagingError("Writer contract has invalid table descriptor fields")
    required_descriptor_set = set(required_descriptor)
    for table in table_names:
        descriptor = tables[table]
        if not isinstance(descriptor, dict):
            raise StagingError(f"Table descriptor must be an object: {table}")
        if set(descriptor) != required_descriptor_set:
            raise StagingError(f"Unsupported descriptor fields for table: {table}")
        expected_path = f"tables/{table}.json"
        if descriptor.get("path") != expected_path:
            raise StagingError(f"Unexpected table payload path for {table}")
        for field in ("sha256", "primary_key_sha256", "schema_sha256"):
            if not isinstance(descriptor.get(field), str) or not SHA256_RE.fullmatch(
                descriptor[field]
            ):
                raise StagingError(f"Invalid {field} for table: {table}")
        if isinstance(descriptor.get("row_count"), bool) or not isinstance(
            descriptor.get("row_count"), int
        ) or descriptor["row_count"] < 0:
            raise StagingError(f"Invalid row_count for table: {table}")
        primary_key = descriptor.get("primary_key")
        columns = descriptor.get("columns")
        foreign_keys = descriptor.get("foreign_keys")
        if not isinstance(primary_key, list) or not primary_key or any(
            not isinstance(item, str) or not item for item in primary_key
        ):
            raise StagingError(f"Invalid primary key for table: {table}")
        if not isinstance(columns, list) or not columns or any(
            not isinstance(column, dict) for column in columns
        ):
            raise StagingError(f"Invalid columns for table: {table}")
        if not isinstance(foreign_keys, list) or any(
            not isinstance(foreign_key, dict) for foreign_key in foreign_keys
        ):
            raise StagingError(f"Invalid foreign_keys for table: {table}")
        column_names = [column.get("name") for column in columns]
        if any(not isinstance(name, str) or not name for name in column_names):
            raise StagingError(f"Invalid column name for table: {table}")
        if len(column_names) != len(set(column_names)) or "project_id" not in column_names:
            raise StagingError(f"Unsupported column inventory for table: {table}")
        if not set(primary_key).issubset(column_names):
            raise StagingError(f"Primary key references an unknown column: {table}")
        schema_payload = _canonical_json(
            {
                "columns": columns,
                "foreign_keys": foreign_keys,
                "primary_key": primary_key,
            }
        )
        if _sha256(schema_payload) != descriptor["schema_sha256"]:
            raise StagingError(f"Schema checksum mismatch: {table}")

    _validate_core_references(manifest, contract)
    for field in (
        "tables_sha256",
        "core_references_sha256",
        "schema_fingerprint",
        "semantic_root_sha256",
    ):
        if not isinstance(manifest.get(field), str) or not SHA256_RE.fullmatch(manifest[field]):
            raise StagingError(f"Manifest {field} is invalid")


def _validate_core_references(manifest: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    references = manifest.get("core_references")
    if not isinstance(references, list) or any(not isinstance(item, dict) for item in references):
        raise StagingError("Manifest core_references must be an array of objects")
    required_fields = contract.get("required_core_reference_fields")
    if not isinstance(required_fields, list) or not required_fields or any(
        not isinstance(item, str) for item in required_fields
    ):
        raise StagingError("Writer contract has invalid core reference fields")
    expected_fields = set(required_fields)
    table_names = set(_contract_tables(contract))
    previous_key: tuple[str, bytes, str, str, str] | None = None
    for index, reference in enumerate(references):
        if set(reference) != expected_fields:
            raise StagingError(f"Unsupported Core reference fields at index {index}")
        source_table = reference.get("source_table")
        source_primary_key = reference.get("source_primary_key")
        if source_table not in table_names or not isinstance(source_primary_key, dict):
            raise StagingError(f"Invalid Core reference source at index {index}")
        for field in ("source_field", "entity_type", "entity_id", "target_table"):
            if not isinstance(reference.get(field), str) or not reference[field]:
                raise StagingError(f"Invalid Core reference {field} at index {index}")
        fingerprint = reference.get("snapshot_fingerprint")
        if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
            raise StagingError(f"Invalid Core reference fingerprint at index {index}")
        if not isinstance(reference.get("snapshot_metadata"), dict):
            raise StagingError(f"Invalid Core reference metadata at index {index}")
        if reference.get("resolution_status") != "resolved":
            raise StagingError(f"Unresolved Core reference at index {index}")
        entity_type = str(reference["entity_type"])
        expected_target_table = _CORE_ENTITY_TABLES.get(entity_type)
        if expected_target_table is None:
            raise StagingError(
                f"Unsupported Core reference entity_type at index {index}: {entity_type}"
            )
        if reference["target_table"] != expected_target_table:
            raise StagingError(
                f"Core reference {index} target_table does not match entity_type"
            )
        key = _core_reference_key(reference)
        if previous_key is not None and key < previous_key:
            raise StagingError("Core references are not in canonical order")
        previous_key = key


def _validate_core_reference_sources(
    manifest: Mapping[str, Any], rows: Mapping[str, list[dict[str, Any]]]
) -> None:
    descriptors = manifest["tables"]
    expected = Counter(_derive_expected_core_reference_keys(rows, descriptors))
    actual = Counter(
        _core_reference_key(reference) for reference in manifest["core_references"]
    )
    if actual != expected:
        missing = sorted((expected - actual).elements())
        extra = sorted((actual - expected).elements())
        raise StagingError(
            "Core reference key set does not match frozen v1 Writer rows"
            + (f"; missing={_format_reference_keys(missing)}" if missing else "")
            + (f"; extra={_format_reference_keys(extra)}" if extra else "")
        )
    for index, reference in enumerate(manifest["core_references"]):
        table = str(reference["source_table"])
        primary_key = list(descriptors[table]["primary_key"])
        supplied_key = reference["source_primary_key"]
        if set(supplied_key) != set(primary_key):
            raise StagingError(f"Core reference {index} has an invalid source primary key")
        source_row = next(
            (
                row
                for row in rows[table]
                if all(row[field] == supplied_key[field] for field in primary_key)
            ),
            None,
        )
        if source_row is None:
            raise StagingError(f"Core reference {index} points to a missing Writer row")
        source_field = str(reference["source_field"])
        if not _source_field_contains_entity(
            source_row, source_field, str(reference["entity_id"])
        ):
            raise StagingError(f"Core reference {index} does not match its Writer row")
        expected_version = source_row.get("source_version") or source_row.get(
            "target_version"
        )
        if reference["source_version"] != expected_version:
            raise StagingError(f"Core reference {index} has inconsistent source_version")
        if reference["stored_content_hash"] != source_row.get("content_hash"):
            raise StagingError(f"Core reference {index} has inconsistent stored_content_hash")


def _core_reference_key(
    reference: Mapping[str, Any],
) -> tuple[str, bytes, str, str, str]:
    return (
        str(reference["source_table"]),
        _canonical_json(reference["source_primary_key"]),
        str(reference["source_field"]),
        str(reference["entity_type"]),
        str(reference["entity_id"]),
    )


def _expected_reference_key(
    table: str,
    row: Mapping[str, Any],
    field: str,
    entity_type: str,
    entity_id: str,
    descriptors: Mapping[str, Mapping[str, Any]],
) -> tuple[str, bytes, str, str, str]:
    if entity_type not in _CORE_ENTITY_TABLES:
        raise StagingError(
            f"Writer row {table} references unsupported Core entity_type {entity_type!r}"
        )
    primary_key = descriptors[table]["primary_key"]
    return (
        table,
        _canonical_json({column: row[column] for column in primary_key}),
        field,
        entity_type,
        entity_id,
    )


def _derive_expected_core_reference_keys(
    rows: Mapping[str, list[dict[str, Any]]],
    descriptors: Mapping[str, Mapping[str, Any]],
) -> list[tuple[str, bytes, str, str, str]]:
    """Reproduce the frozen Core v1 exporter reference-selection rules."""

    expected: list[tuple[str, bytes, str, str, str]] = []

    def add(
        table: str,
        row: Mapping[str, Any],
        field: str,
        entity_type: str,
        entity_id: Any,
    ) -> None:
        key = _expected_reference_key(
            table,
            row,
            field,
            entity_type,
            str(entity_id),
            descriptors,
        )
        expected.append(key)

    for table, field, entity_type in _DIRECT_CORE_REFERENCES:
        for row in rows.get(table, []):
            entity_id = row.get(field)
            if entity_id:
                add(table, row, field, entity_type, entity_id)

    for row in rows.get("manuscript_units", []):
        artifact_ref = row.get("artifact_ref")
        if isinstance(artifact_ref, str) and artifact_ref.startswith(("art_", "fig_")):
            entity_type = "artifact" if artifact_ref.startswith("art_") else "figure"
            add("manuscript_units", row, "artifact_ref", entity_type, artifact_ref)

    for row in rows.get("manuscript_planning_evidence_bindings", []):
        entity_type = str(row.get("entity_type"))
        if entity_type not in _INTERNAL_WRITER_ENTITY_TYPES:
            add(
                "manuscript_planning_evidence_bindings",
                row,
                "entity_id",
                entity_type,
                row.get("entity_id"),
            )

    for table in (
        "manuscript_planning_artifact_versions",
        "manuscript_planning_promotion_events",
        "manuscript_evaluation_events",
    ):
        for row in rows.get(table, []):
            promoted = row.get("promotion_target_type") is not None
            entity_type = row.get("promotion_target_type") or row.get("target_type")
            entity_id = row.get("promotion_target_id") or row.get("target_id")
            if entity_type and entity_id and entity_type not in _INTERNAL_WRITER_ENTITY_TYPES:
                field = "promotion_target_id" if promoted else "target_id"
                add(table, row, field, str(entity_type), entity_id)

    for row in rows.get("semantic_patch_context_manifests", []):
        selected_context = _parse_json_text(
            row.get("selected_context"),
            f"semantic context manifest {row.get('id')!r} selected_context",
        )
        if not isinstance(selected_context, list):
            raise StagingError(
                f"Semantic context manifest {row.get('id')!r} selected_context must be an array"
            )
        for selection in selected_context:
            if not isinstance(selection, dict) or not selection.get("entity_id"):
                raise StagingError(
                    f"Semantic context manifest {row.get('id')!r} has invalid selected_context"
                )
            entity_id = str(selection["entity_id"])
            entity_type = _ENTITY_TYPES_BY_ID_PREFIX.get(entity_id.partition("_")[0])
            if entity_type is None:
                raise StagingError(
                    f"Semantic context manifest {row.get('id')!r} references "
                    f"unknown entity ID {entity_id!r}"
                )
            if entity_type not in _INTERNAL_WRITER_ENTITY_TYPES:
                add(
                    "semantic_patch_context_manifests",
                    row,
                    "selected_context.entity_id",
                    entity_type,
                    entity_id,
                )
    return expected


def _parse_json_text(value: Any, label: str) -> Any:
    if not isinstance(value, str):
        raise StagingError(f"{label} is not JSON text")
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise StagingError(f"{label} contains malformed JSON") from exc


def _format_reference_keys(
    keys: Sequence[tuple[str, bytes, str, str, str]],
) -> list[str]:
    return [
        f"{table}:{field}:{entity_type}:{entity_id}"
        for table, _primary_key, field, entity_type, entity_id in keys
    ]


def _source_field_contains_entity(
    row: Mapping[str, Any], source_field: str, entity_id: str
) -> bool:
    head, separator, tail = source_field.partition(".")
    if head not in row:
        return False
    if not separator:
        return row[head] == entity_id
    value = row[head]
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return False
    candidates = value if isinstance(value, list) else [value]
    return any(isinstance(item, dict) and item.get(tail) == entity_id for item in candidates)


def _validate_table_rows(
    table: str,
    raw_rows: list[Any],
    descriptor: Mapping[str, Any],
    project_id: str,
    contract: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if len(raw_rows) != descriptor["row_count"]:
        raise StagingError(f"Row count mismatch: {table}")
    columns = list(descriptor["columns"])
    column_names = [str(column["name"]) for column in columns]
    column_by_name = {str(column["name"]): column for column in columns}
    primary_key = [str(item) for item in descriptor["primary_key"]]
    rows: list[dict[str, Any]] = []
    seen_keys: set[bytes] = set()
    previous_sort_key: tuple[tuple[int, Any], ...] | None = None
    nullable_project_tables = set(contract.get("nullable_project_id_tables", []))
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, dict) or set(raw_row) != set(column_names):
            raise StagingError(f"Row {index} has unsupported fields: {table}")
        row = dict(raw_row)
        if row.get("project_id") != project_id and not (
            table in nullable_project_tables and row.get("project_id") is None
        ):
            raise StagingError(f"Row {index} crosses project scope: {table}")
        for name in column_names:
            _validate_sqlite_value(table, index, name, row[name], column_by_name[name])
        key_values = [row[name] for name in primary_key]
        if any(value is None for value in key_values):
            raise StagingError(f"Row {index} has a null primary key: {table}")
        key_payload = _canonical_json(key_values)
        if key_payload in seen_keys:
            raise StagingError(f"Duplicate primary key in table: {table}")
        seen_keys.add(key_payload)
        sort_key = tuple(_sqlite_sort_key(value) for value in key_values)
        if previous_sort_key is not None and sort_key < previous_sort_key:
            raise StagingError(f"Rows are not ordered by primary key: {table}")
        previous_sort_key = sort_key
        rows.append(row)
    return rows


def _sqlite_sort_key(value: Any) -> tuple[int, Any]:
    if value is None:
        return (0, "")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (1, value)
    if isinstance(value, str):
        return (2, value)
    return (3, _canonical_json(value))


def _validate_sqlite_value(
    table: str,
    index: int,
    name: str,
    value: Any,
    column: Mapping[str, Any],
) -> None:
    not_null = bool(column.get("notnull")) or bool(column.get("pk"))
    if value is None:
        if not_null:
            raise StagingError(f"Null value for {table}[{index}].{name}")
        return
    declared_type = str(column.get("type") or "").upper()
    if "INT" in declared_type:
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif any(token in declared_type for token in ("REAL", "FLOA", "DOUB")):
        valid = isinstance(value, (int, float)) and not isinstance(value, bool)
    elif "BLOB" in declared_type:
        valid = (
            isinstance(value, dict)
            and set(value) == {"$rka_base64"}
            and isinstance(value["$rka_base64"], str)
        )
    else:
        valid = isinstance(value, str)
    if not valid:
        raise StagingError(
            f"Unsupported SQLite value for {table}[{index}].{name}: {declared_type or 'TEXT'}"
        )


def _validate_internal_references(
    rows: Mapping[str, list[dict[str, Any]]],
    descriptors: Mapping[str, Mapping[str, Any]],
    table_names: Sequence[str],
) -> int:
    table_set = set(table_names)
    checked = 0
    for source_table in table_names:
        grouped: dict[int, list[Mapping[str, Any]]] = {}
        for foreign_key in descriptors[source_table]["foreign_keys"]:
            fk_id = foreign_key.get("id")
            if isinstance(fk_id, bool) or not isinstance(fk_id, int):
                raise StagingError(f"Invalid foreign-key descriptor: {source_table}")
            grouped.setdefault(fk_id, []).append(foreign_key)
        for group in grouped.values():
            ordered = sorted(group, key=lambda item: int(item.get("seq", 0)))
            target_table = ordered[0].get("table")
            if target_table not in table_set:
                continue
            source_columns = [item.get("from") for item in ordered]
            target_columns = [item.get("to") for item in ordered]
            if any(not isinstance(item, str) or not item for item in source_columns + target_columns):
                raise StagingError(f"Unsupported foreign-key descriptor: {source_table}")
            target_values = {
                _canonical_json([target[column] for column in target_columns])
                for target in rows[str(target_table)]
            }
            for row in rows[source_table]:
                values = [row[column] for column in source_columns]
                if any(value is None for value in values):
                    continue
                checked += 1
                if _canonical_json(values) not in target_values:
                    raise StagingError(
                        f"Missing internal reference: {source_table} -> {target_table}"
                    )

    def check_logical_target(entity_type: Any, entity_id: Any, source: str) -> None:
        nonlocal checked
        target_table = _LOGICAL_INTERNAL_TARGETS.get(str(entity_type))
        if target_table is None:
            return
        if target_table not in table_set:
            raise StagingError(
                f"Internal logical target table is absent from the contract: {target_table}"
            )
        if list(descriptors[target_table]["primary_key"]) != ["id"]:
            raise StagingError(
                f"Internal logical target must use id as its primary key: {target_table}"
            )
        checked += 1
        target_ids = {row.get("id") for row in rows[target_table]}
        if entity_id not in target_ids:
            raise StagingError(
                f"Missing internal polymorphic reference: {source} -> {target_table}"
            )

    for binding in rows.get("manuscript_planning_evidence_bindings", []):
        check_logical_target(
            binding.get("entity_type"),
            binding.get("entity_id"),
            "manuscript_planning_evidence_bindings",
        )

    for source_table in (
        "manuscript_planning_artifact_versions",
        "manuscript_planning_promotion_events",
        "manuscript_evaluation_events",
    ):
        for row in rows.get(source_table, []):
            entity_type = row.get("promotion_target_type") or row.get("target_type")
            entity_id = row.get("promotion_target_id") or row.get("target_id")
            if entity_type and entity_id:
                check_logical_target(entity_type, entity_id, source_table)

    for row in rows.get("semantic_patch_context_manifests", []):
        selected_context = _parse_json_text(
            row.get("selected_context"),
            f"semantic context manifest {row.get('id')!r} selected_context",
        )
        if not isinstance(selected_context, list):
            raise StagingError(
                f"Semantic context manifest {row.get('id')!r} selected_context must be an array"
            )
        for selection in selected_context:
            if not isinstance(selection, dict) or not selection.get("entity_id"):
                raise StagingError(
                    f"Semantic context manifest {row.get('id')!r} has invalid selected_context"
                )
            entity_id = str(selection["entity_id"])
            entity_type = _ENTITY_TYPES_BY_ID_PREFIX.get(entity_id.partition("_")[0])
            if entity_type is None:
                raise StagingError(
                    f"Semantic context manifest {row.get('id')!r} references "
                    f"unknown entity ID {entity_id!r}"
                )
            check_logical_target(
                entity_type,
                entity_id,
                "semantic_patch_context_manifests.selected_context",
            )

    versions = {
        str(row.get("id")): row
        for row in rows.get("manuscript_planning_artifact_versions", [])
    }
    for artifact in rows.get("manuscript_planning_artifacts", []):
        current_version = int(artifact.get("current_version") or 0)
        current_version_id = artifact.get("current_version_id")
        if current_version == 0 and current_version_id is None:
            continue
        checked += 1
        version = versions.get(str(current_version_id))
        if (
            version is None
            or version.get("artifact_id") != artifact.get("id")
            or int(version.get("version") or 0) != current_version
        ):
            raise StagingError(
                "Missing internal current-version reference: "
                "manuscript_planning_artifacts -> "
                "manuscript_planning_artifact_versions"
            )

    attestation_ids = {
        str(row.get("id"))
        for row in rows.get("reference_validation_attestations", [])
    }
    for issue in rows.get("reference_validation_migration_issues", []):
        checked += 1
        if str(issue.get("attestation_id")) not in attestation_ids:
            raise StagingError(
                "Missing internal attestation reference: "
                "reference_validation_migration_issues -> "
                "reference_validation_attestations"
            )
    return checked


def _validate_aggregates(manifest: dict[str, Any], contract: dict[str, Any]) -> None:
    table_names = _contract_tables(contract)
    expected_rows = sum(manifest["tables"][table]["row_count"] for table in table_names)
    if manifest["row_count"] != expected_rows:
        raise StagingError("Manifest aggregate row_count mismatch")
    table_roots = {
        table: {
            "row_count": manifest["tables"][table]["row_count"],
            "sha256": manifest["tables"][table]["sha256"],
            "primary_key_sha256": manifest["tables"][table]["primary_key_sha256"],
            "schema_sha256": manifest["tables"][table]["schema_sha256"],
        }
        for table in table_names
    }
    expected_tables_hash = _sha256(_canonical_json(table_roots))
    if manifest["tables_sha256"] != expected_tables_hash:
        raise StagingError("Manifest tables_sha256 mismatch")
    expected_schema = _sha256(
        _canonical_json(
            {table: manifest["tables"][table]["schema_sha256"] for table in table_names}
        )
    )
    if manifest["schema_fingerprint"] != expected_schema:
        raise StagingError("Manifest schema_fingerprint mismatch")

    supported = contract.get("schema_fingerprint")
    if not isinstance(supported, str) or not SHA256_RE.fullmatch(supported):
        raise StagingError("Writer v1 contract does not freeze a schema fingerprint")
    if manifest["schema_fingerprint"] != supported:
        raise StagingError("Bundle schema fingerprint is unsupported by Writer v1")

    core_hash = _sha256(_canonical_json(manifest["core_references"]))
    if manifest["core_references_sha256"] != core_hash:
        raise StagingError("Manifest core_references_sha256 mismatch")
    root_payload = {
        "contract": manifest["contract"],
        "project_id": manifest["source"]["project_id"],
        "schema_fingerprint": manifest["schema_fingerprint"],
        "tables_sha256": manifest["tables_sha256"],
        "core_references_sha256": core_hash,
    }
    expected_root = _sha256(_canonical_json(root_payload))
    if manifest["semantic_root_sha256"] != expected_root:
        raise StagingError("Manifest semantic_root_sha256 mismatch")


def _stage_manifest(inspected: _InspectedBundle) -> dict[str, Any]:
    return {
        "authority_switched": False,
        "contract": inspected.manifest["contract"],
        "project_id": inspected.project_id,
        "record_format": "canonical-jsonl/v1",
        "report_contract": EQUIVALENCE_CONTRACT,
        "schema_fingerprint": inspected.manifest["schema_fingerprint"],
        "semantic_root_sha256": inspected.semantic_root_sha256,
        "table_count": inspected.manifest["table_count"],
        "tables": {
            table: {
                "path": f"records/{table}.jsonl",
                "primary_key": inspected.manifest["tables"][table]["primary_key"],
                "row_count": inspected.manifest["tables"][table]["row_count"],
                "source_sha256": inspected.manifest["tables"][table]["sha256"],
            }
            for table in _contract_tables(inspected.contract)
        },
        "tables_sha256": inspected.manifest["tables_sha256"],
    }


def _equivalence_report(
    inspected: _InspectedBundle,
    staged_rows: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    table_names = _contract_tables(inspected.contract)
    tables: dict[str, Any] = {}
    for table in table_names:
        source_descriptor = inspected.manifest["tables"][table]
        staged_payload = _canonical_json(staged_rows[table])
        staged_sha256 = _sha256(staged_payload)
        key_fields = source_descriptor["primary_key"]
        primary_keys = [[row[field] for field in key_fields] for row in staged_rows[table]]
        tables[table] = {
            "equivalent": (
                len(staged_rows[table]) == source_descriptor["row_count"]
                and staged_sha256 == source_descriptor["sha256"]
            ),
            "primary_keys_sha256": _sha256(_canonical_json(primary_keys)),
            "row_count": len(staged_rows[table]),
            "source_sha256": source_descriptor["sha256"],
            "staged_sha256": staged_sha256,
        }
    if not all(item["equivalent"] for item in tables.values()):
        raise StagingError("Staged records are not equivalent to the source bundle")

    core_references = inspected.manifest["core_references"]
    return {
        "authority_switched": False,
        "categories": {
            "bindings": _category_digest(staged_rows, _BINDING_TABLES),
            "identifiers": _identifier_digest(staged_rows, inspected.manifest["tables"]),
            "ratifications": _category_digest(staged_rows, _RATIFICATION_TABLES),
            "revisions": _revision_digest(staged_rows),
            "source_references": _category_digest(staged_rows, _SOURCE_REFERENCE_TABLES),
        },
        "contract": EQUIVALENCE_CONTRACT,
        "core_references": {
            "count": len(core_references),
            "resolution": "all_resolved",
            "sha256": _sha256(_canonical_json(core_references)),
        },
        "internal_references": {
            "checked": inspected.internal_reference_count,
            "unresolved": 0,
        },
        "project_id": inspected.project_id,
        "row_count": sum(len(staged_rows[table]) for table in table_names),
        "schema_fingerprint": inspected.manifest["schema_fingerprint"],
        "semantic_root_sha256": inspected.semantic_root_sha256,
        "status": "equivalent",
        "table_count": len(table_names),
        "tables": tables,
        "tables_sha256": inspected.manifest["tables_sha256"],
    }


def _category_digest(
    rows: Mapping[str, list[dict[str, Any]]], tables: Iterable[str]
) -> dict[str, Any]:
    selected = {table: rows.get(table, []) for table in sorted(tables)}
    return {
        "row_count": sum(len(table_rows) for table_rows in selected.values()),
        "sha256": _sha256(_canonical_json(selected)),
    }


def _identifier_digest(
    rows: Mapping[str, list[dict[str, Any]]],
    descriptors: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    identities = {
        table: [
            [row[field] for field in descriptors[table]["primary_key"]]
            for row in rows[table]
        ]
        for table in sorted(rows)
    }
    return {
        "row_count": sum(len(values) for values in identities.values()),
        "sha256": _sha256(_canonical_json(identities)),
    }


def _revision_digest(rows: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    revisions: list[dict[str, Any]] = []
    for table in sorted(rows):
        for row in rows[table]:
            values = {
                key: value
                for key, value in sorted(row.items())
                if key in {"revision", "version"} or key.endswith("_revision")
            }
            if values:
                revisions.append({"table": table, "values": values})
    return {
        "row_count": len(revisions),
        "sha256": _sha256(_canonical_json(revisions)),
    }


def _verify_staged_directory(bundle_path: Path, directory: Path) -> dict[str, Any]:
    if not directory.is_dir() or directory.is_symlink():
        raise StagingError(f"Staging directory is missing or unsafe: {directory}")
    expected_entries = {
        COMPLETE_MARKER,
        "equivalence-report.json",
        "records",
        "source-bundle.zip",
        "stage-manifest.json",
    }
    actual_entries = {path.name for path in directory.iterdir()}
    if actual_entries != expected_entries:
        raise StagingError("Staging directory inventory mismatch")
    source_bundle = directory / "source-bundle.zip"
    _reject_symlink(source_bundle, "staged source bundle")
    source = _inspect_bundle(bundle_path)
    staged_source = _inspect_bundle(source_bundle)
    if source.file_sha256 != staged_source.file_sha256:
        raise StagingError("Staged source bundle differs from the requested bundle")

    stage_manifest = _load_json_file(directory / "stage-manifest.json")
    if stage_manifest != _stage_manifest(source):
        raise StagingError("Staging manifest mismatch")
    records_root = directory / "records"
    if not records_root.is_dir() or records_root.is_symlink():
        raise StagingError("Staged records directory is missing or unsafe")
    expected_record_names = {
        f"{table}.jsonl" for table in _contract_tables(source.contract)
    }
    actual_record_names = {path.name for path in records_root.iterdir() if path.is_file()}
    if actual_record_names != expected_record_names or any(
        path.is_dir() or path.is_symlink() for path in records_root.iterdir()
    ):
        raise StagingError("Staged record inventory mismatch")

    staged_rows: dict[str, list[dict[str, Any]]] = {}
    for table in _contract_tables(source.contract):
        staged_rows[table] = _load_jsonl(records_root / f"{table}.jsonl")
        _validate_table_rows(
            table,
            staged_rows[table],
            source.manifest["tables"][table],
            source.project_id,
            source.contract,
        )
    internal_count = _validate_internal_references(
        staged_rows, source.manifest["tables"], _contract_tables(source.contract)
    )
    if internal_count != source.internal_reference_count:
        raise StagingError("Staged internal reference count mismatch")

    expected_report = _equivalence_report(source, staged_rows)
    expected_payload = _canonical_json(expected_report) + b"\n"
    report_path = directory / "equivalence-report.json"
    _reject_symlink(report_path, "equivalence report")
    try:
        actual_payload = report_path.read_bytes()
    except OSError as exc:
        raise StagingError(f"Cannot read equivalence report: {exc}") from exc
    if actual_payload != expected_payload:
        raise StagingError("Stored equivalence report is not deterministic or current")
    complete_path = directory / COMPLETE_MARKER
    _reject_symlink(complete_path, "completion marker")
    try:
        marker = complete_path.read_text(encoding="ascii")
    except OSError as exc:
        raise StagingError(f"Cannot read completion marker: {exc}") from exc
    if marker != _sha256(expected_payload) + "\n":
        raise StagingError("Completion marker checksum mismatch")
    return expected_report


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    _reject_symlink(path, "staged record file")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise StagingError(f"Cannot read staged records: {exc}") from exc
    rows: list[dict[str, Any]] = []
    if not payload:
        return rows
    for number, line in enumerate(payload.splitlines(keepends=True), start=1):
        if not line.endswith(b"\n") or line == b"\n":
            raise StagingError(f"Malformed canonical JSONL at {path.name}:{number}")
        value = _load_json_bytes(line[:-1], f"{path.name}:{number}")
        if not isinstance(value, dict) or line != _canonical_json(value) + b"\n":
            raise StagingError(f"Non-canonical JSONL at {path.name}:{number}")
        rows.append(value)
    return rows


def _prepare_staging_root(path: Path, create: bool = True) -> Path:
    expanded = path.expanduser()
    _reject_symlink(expanded, "staging root")
    if create:
        expanded.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        root = expanded.resolve(strict=True)
    except FileNotFoundError as exc:
        raise StagingError(f"Staging root not found: {expanded}") from exc
    if not root.is_dir():
        raise StagingError(f"Staging root is not a directory: {root}")
    return root


def _reject_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise StagingError(f"{label.capitalize()} must not be a symbolic link: {path}")


def _load_json_file(path: Path) -> Any:
    _reject_symlink(path, "JSON file")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StagingError(f"Cannot read JSON file {path}: {exc}") from exc


def _load_json_bytes(payload: bytes, label: str) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StagingError(f"Invalid JSON in {label}: {exc}") from exc


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _write_json(path: Path, value: Any) -> None:
    _write_file(path, _canonical_json(value) + b"\n")


def _write_file(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    finally:
        os.close(descriptor)


def _copy_file(source: Path, destination: Path) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(destination, flags, 0o600)
    try:
        with source.open("rb") as input_file, os.fdopen(
            descriptor, "wb", closefd=False
        ) as output_file:
            for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
                output_file.write(chunk)
            output_file.flush()
            os.fsync(output_file.fileno())
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rka-writer-staging",
        description="Inspect and stage legacy RKA Core Writer bundles without switching authority.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="validate a bundle without writing")
    inspect_parser.add_argument("bundle", type=Path)
    for command in ("stage", "verify"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("bundle", type=Path)
        command_parser.add_argument("--staging-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect_bundle(args.bundle)
        elif args.command == "stage":
            result = stage_bundle(args.bundle, args.staging_root)
        else:
            result = verify_stage(args.bundle, args.staging_root)
    except StagingError as exc:
        print(
            json.dumps(
                {"authority_switched": False, "error": str(exc), "status": "rejected"},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
