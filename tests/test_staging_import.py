"""Standalone legacy Writer staging contract tests."""

from __future__ import annotations

import base64
import errno
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "rka-legacy-writer-export-v1.json"
GOLDEN_BUNDLE_B64 = ROOT / "tests" / "legacy_writer_export_v1.zip.b64"
sys.path.insert(0, str(ROOT))

import rka_writer_staging as staging


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _rewrite_manifest(bundle: Path, update) -> None:
    with zipfile.ZipFile(bundle) as source:
        members = {name: source.read(name) for name in source.namelist()}
    manifest = json.loads(members["manifest.json"])
    update(manifest)
    members["manifest.json"] = _canonical(manifest)
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, payload in members.items():
            target.writestr(name, payload)


def _refresh_manifest_digests(manifest: dict) -> None:
    manifest["core_references_sha256"] = _sha(_canonical(manifest["core_references"]))
    manifest["semantic_root_sha256"] = _sha(
        _canonical(
            {
                "contract": manifest["contract"],
                "project_id": manifest["source"]["project_id"],
                "schema_fingerprint": manifest["schema_fingerprint"],
                "tables_sha256": manifest["tables_sha256"],
                "core_references_sha256": manifest["core_references_sha256"],
            }
        )
    )


def _column(cid: int, name: str, declared_type: str, *, pk: int = 0) -> dict:
    return {
        "cid": cid,
        "name": name,
        "type": declared_type,
        "notnull": 0,
        "dflt_value": None,
        "pk": pk,
    }


def _descriptor(table: str, rows: list[dict]) -> dict:
    if table == "manuscripts":
        columns = [
            _column(0, "id", "TEXT", pk=1),
            _column(1, "project_id", "TEXT"),
            _column(2, "legacy_journal_id", "TEXT"),
        ]
        primary_key = ["id"]
    else:
        columns = [
            _column(0, "legacy_journal_id", "TEXT", pk=1),
            _column(1, "project_id", "TEXT"),
        ]
        primary_key = ["legacy_journal_id"]
    foreign_keys: list[dict] = []
    schema_payload = _canonical(
        {
            "columns": columns,
            "foreign_keys": foreign_keys,
            "primary_key": primary_key,
        }
    )
    payload = _canonical(rows)
    primary_keys = [{field: row[field] for field in primary_key} for row in rows]
    return {
        "path": f"tables/{table}.json",
        "row_count": len(rows),
        "sha256": _sha(payload),
        "primary_key_sha256": _sha(_canonical(primary_keys)),
        "schema_sha256": _sha(schema_payload),
        "primary_key": primary_key,
        "columns": columns,
        "foreign_keys": foreign_keys,
    }


def _simple_descriptor(
    table: str,
    rows: list[dict],
    columns: list[dict],
) -> dict:
    primary_key = [column["name"] for column in columns if column.get("pk")]
    schema_payload = _canonical(
        {"columns": columns, "foreign_keys": [], "primary_key": primary_key}
    )
    payload = _canonical(rows)
    primary_keys = [{field: row[field] for field in primary_key} for row in rows]
    return {
        "path": f"tables/{table}.json",
        "row_count": len(rows),
        "sha256": _sha(payload),
        "primary_key_sha256": _sha(_canonical(primary_keys)),
        "schema_sha256": _sha(schema_payload),
        "primary_key": primary_key,
        "columns": columns,
        "foreign_keys": [],
    }


def _write_custom_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rows: dict[str, list[dict]],
    descriptors: dict[str, dict],
    core_references: list[dict] | None = None,
) -> Path:
    schema_fingerprint = _sha(
        _canonical(
            {table: descriptor["schema_sha256"] for table, descriptor in descriptors.items()}
        )
    )
    base_contract = json.loads(CONTRACT.read_text())
    contract = {
        **base_contract,
        "schema_fingerprint": schema_fingerprint,
        "tables": list(rows),
    }
    contract_path = tmp_path / "custom-contract.json"
    contract_path.write_bytes(_canonical(contract))
    monkeypatch.setattr(staging, "CONTRACT_PATH", contract_path)
    table_roots = {
        table: {
            key: descriptor[key]
            for key in ("row_count", "sha256", "primary_key_sha256", "schema_sha256")
        }
        for table, descriptor in descriptors.items()
    }
    manifest = {
        "contract": contract["contract"],
        "format_version": contract["format_version"],
        "schema_fingerprint": schema_fingerprint,
        "source": {"project_id": "prj_test", "core_version": "test"},
        "authority": {"authority_switched": False},
        "required_tables": list(rows),
        "tables": descriptors,
        "table_count": len(rows),
        "row_count": sum(len(table_rows) for table_rows in rows.values()),
        "tables_sha256": _sha(_canonical(table_roots)),
        "core_references": core_references or [],
    }
    _refresh_manifest_digests(manifest)
    bundle = tmp_path / "custom-writer.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for table, table_rows in rows.items():
            archive.writestr(f"tables/{table}.json", _canonical(table_rows))
        archive.writestr("manifest.json", _canonical(manifest))
    return bundle


@pytest.fixture
def bundle_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def make(
        *, unresolved: bool = False, wrong_nullable_scope: bool = False
    ) -> tuple[Path, dict]:
        project_id = "prj_test"
        rows = {
            "manuscripts": [
                {
                    "id": "man_1",
                    "project_id": project_id,
                    "legacy_journal_id": "jrn_1",
                }
            ],
            "manuscript_migration_issues": [
                {
                    "legacy_journal_id": "jrn_1",
                    "project_id": "prj_other" if wrong_nullable_scope else None,
                }
            ],
        }
        descriptors = {
            table: _descriptor(table, table_rows) for table, table_rows in rows.items()
        }
        schema_fingerprint = _sha(
            _canonical(
                {table: descriptor["schema_sha256"] for table, descriptor in descriptors.items()}
            )
        )
        base_contract = json.loads(CONTRACT.read_text())
        contract = {
            **base_contract,
            "schema_fingerprint": schema_fingerprint,
            "tables": list(rows),
        }
        contract_path = tmp_path / "contract.json"
        contract_path.write_bytes(_canonical(contract))
        monkeypatch.setattr(staging, "CONTRACT_PATH", contract_path)

        manuscript_reference = {
            "source_table": "manuscripts",
            "source_primary_key": {"id": "man_1"},
            "source_field": "legacy_journal_id",
            "entity_type": "journal",
            "entity_id": "jrn_1",
            "target_table": "journal",
            "source_version": None,
            "stored_content_hash": None,
            "snapshot_fingerprint": _sha(_canonical({"id": "jrn_1"})),
            "snapshot_metadata": {"revision": 1},
            "resolution_status": "missing" if unresolved else "resolved",
        }
        migration_reference = {
            **manuscript_reference,
            "source_table": "manuscript_migration_issues",
            "source_primary_key": {"legacy_journal_id": "jrn_1"},
        }
        core_references = [migration_reference, manuscript_reference]
        table_roots = {
            table: {
                key: descriptor[key]
                for key in (
                    "row_count",
                    "sha256",
                    "primary_key_sha256",
                    "schema_sha256",
                )
            }
            for table, descriptor in descriptors.items()
        }
        tables_sha256 = _sha(_canonical(table_roots))
        core_references_sha256 = _sha(_canonical(core_references))
        semantic_root_sha256 = _sha(
            _canonical(
                {
                    "contract": contract["contract"],
                    "project_id": project_id,
                    "schema_fingerprint": schema_fingerprint,
                    "tables_sha256": tables_sha256,
                    "core_references_sha256": core_references_sha256,
                }
            )
        )
        manifest = {
            "contract": contract["contract"],
            "format_version": contract["format_version"],
            "schema_fingerprint": schema_fingerprint,
            "source": {"project_id": project_id, "core_version": "test"},
            "authority": {"authority_switched": False},
            "required_tables": list(rows),
            "tables": descriptors,
            "table_count": len(rows),
            "row_count": sum(len(table_rows) for table_rows in rows.values()),
            "tables_sha256": tables_sha256,
            "core_references": core_references,
            "core_references_sha256": core_references_sha256,
            "semantic_root_sha256": semantic_root_sha256,
        }
        bundle = tmp_path / "writer.zip"
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for table, table_rows in rows.items():
                archive.writestr(f"tables/{table}.json", _canonical(table_rows))
            archive.writestr("manifest.json", _canonical(manifest))
        return bundle, manifest

    return make


def test_contract_copy_freezes_core_v1_shape() -> None:
    contract = json.loads(CONTRACT.read_text())
    assert contract["contract"] == "rka-legacy-writer-export/v1"
    assert contract["schema_fingerprint"] == (
        "9008c196a5da9bc4151f44c9eea9332f994041d2691a2fcb5f3ceb5cf52059ff"
    )
    assert len(contract["tables"]) == 29
    assert contract["nullable_project_id_tables"] == ["manuscript_migration_issues"]
    assert "core_references_sha256" in contract["required_manifest_fields"]


def test_core_generated_golden_bundle_inspect_stage_verify(
    tmp_path: Path,
) -> None:
    """Exercise a checked-in bundle emitted by Core's current v1 exporter."""

    bundle = tmp_path / "golden.rka-writer-export.zip"
    bundle.write_bytes(base64.b64decode(GOLDEN_BUNDLE_B64.read_text(encoding="ascii")))

    inspected = staging.inspect_bundle(bundle)
    assert inspected["table_count"] == 29
    assert inspected["row_count"] == 39
    assert inspected["core_reference_count"] == 20
    assert inspected["internal_reference_count"] == 46

    root = tmp_path / "staging"
    staged = staging.stage_bundle(bundle, root)
    assert staged == staging.verify_stage(bundle, root)
    assert staged["status"] == "equivalent"
    assert staged["core_references"]["resolution"] == "all_resolved"


def test_inspect_stage_verify_and_repeat_are_deterministic(
    bundle_factory, tmp_path: Path
) -> None:
    bundle, manifest = bundle_factory()
    inspected = staging.inspect_bundle(bundle)
    assert inspected["semantic_root_sha256"] == manifest["semantic_root_sha256"]
    assert inspected["core_reference_count"] == 2
    assert inspected["authority_switched"] is False

    root = tmp_path / "staging"
    first = staging.stage_bundle(bundle, root)
    second = staging.stage_bundle(bundle, root)
    verified = staging.verify_stage(bundle, root)
    assert first == second == verified
    assert first["status"] == "equivalent"
    assert first["core_references"]["resolution"] == "all_resolved"
    destination = root / "prj_test" / manifest["semantic_root_sha256"]
    assert json.loads((destination / "records" / "manuscripts.jsonl").read_text())[
        "id"
    ] == "man_1"


@pytest.mark.parametrize("race_errno", [errno.EEXIST, errno.ENOTEMPTY])
def test_concurrent_directory_rename_verifies_the_winner_portably(
    bundle_factory,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    race_errno: int,
) -> None:
    bundle, manifest = bundle_factory()
    root = tmp_path / "staging"
    destination = root / "prj_test" / manifest["semantic_root_sha256"]
    real_rename = staging.os.rename

    def concurrent_winner(source: str | Path, target: str | Path) -> None:
        source_path = Path(source)
        target_path = Path(target)
        shutil.copytree(source_path, target_path)
        raise OSError(race_errno, "simulated concurrent staging winner")

    monkeypatch.setattr(staging.os, "rename", concurrent_winner)
    report = staging.stage_bundle(bundle, root)
    monkeypatch.setattr(staging.os, "rename", real_rename)

    assert destination.is_dir()
    assert report == staging.verify_stage(bundle, root)


def test_unresolved_core_reference_is_rejected(bundle_factory) -> None:
    bundle, _ = bundle_factory(unresolved=True)
    with pytest.raises(staging.StagingError, match="Unresolved Core reference"):
        staging.inspect_bundle(bundle)


def test_missing_expected_core_reference_is_rejected(bundle_factory) -> None:
    bundle, _ = bundle_factory()

    def remove_expected(manifest: dict) -> None:
        manifest["core_references"] = manifest["core_references"][1:]
        _refresh_manifest_digests(manifest)

    _rewrite_manifest(bundle, remove_expected)
    with pytest.raises(staging.StagingError, match="Core reference key set"):
        staging.inspect_bundle(bundle)


def test_core_reference_target_table_must_match_entity_type(bundle_factory) -> None:
    bundle, _ = bundle_factory()

    def change_target(manifest: dict) -> None:
        manifest["core_references"][0]["target_table"] = "claims"
        _refresh_manifest_digests(manifest)

    _rewrite_manifest(bundle, change_target)
    with pytest.raises(staging.StagingError, match="target_table does not match"):
        staging.inspect_bundle(bundle)


def test_duplicate_semantic_context_reference_preserves_multiplicity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = {
        "semantic_patch_context_manifests": [
            {
                "id": "pcm_1",
                "project_id": "prj_test",
                "selected_context": (
                    '[{"entity_id":"jrn_1"},{"entity_id":"jrn_1"}]'
                ),
            }
        ]
    }
    descriptors = {
        "semantic_patch_context_manifests": _simple_descriptor(
            "semantic_patch_context_manifests",
            rows["semantic_patch_context_manifests"],
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
                _column(2, "selected_context", "TEXT"),
            ],
        )
    }
    reference = {
        "source_table": "semantic_patch_context_manifests",
        "source_primary_key": {"id": "pcm_1"},
        "source_field": "selected_context.entity_id",
        "entity_type": "journal",
        "entity_id": "jrn_1",
        "target_table": "journal",
        "source_version": None,
        "stored_content_hash": None,
        "snapshot_fingerprint": _sha(_canonical({"id": "jrn_1"})),
        "snapshot_metadata": {"revision": 1},
        "resolution_status": "resolved",
    }
    bundle = _write_custom_bundle(
        tmp_path,
        monkeypatch,
        rows,
        descriptors,
        core_references=[reference, dict(reference)],
    )

    inspected = staging.inspect_bundle(bundle)

    assert inspected["core_reference_count"] == 2


def test_project_scope_is_fail_closed_except_for_declared_nullable_table(
    bundle_factory,
) -> None:
    bundle, _ = bundle_factory(wrong_nullable_scope=True)
    with pytest.raises(staging.StagingError, match="crosses project scope"):
        staging.inspect_bundle(bundle)


@pytest.mark.parametrize(
    ("entity_type", "target_table"),
    sorted(staging._LOGICAL_INTERNAL_TARGETS.items()),
)
def test_each_internal_logical_type_requires_an_existing_target_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entity_type: str,
    target_table: str,
) -> None:
    binding_rows = [
        {
            "id": "plb_1",
            "project_id": "prj_test",
            "entity_type": entity_type,
            "entity_id": "missing_internal_id",
        }
    ]
    target_rows = [{"id": "present_internal_id", "project_id": "prj_test"}]
    rows = {
        "manuscript_planning_evidence_bindings": binding_rows,
        target_table: target_rows,
    }
    descriptors = {
        "manuscript_planning_evidence_bindings": _simple_descriptor(
            "manuscript_planning_evidence_bindings",
            binding_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
                _column(2, "entity_type", "TEXT"),
                _column(3, "entity_id", "TEXT"),
            ],
        ),
        target_table: _simple_descriptor(
            target_table,
            target_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
            ],
        ),
    }
    bundle = _write_custom_bundle(tmp_path, monkeypatch, rows, descriptors)

    with pytest.raises(staging.StagingError, match="Missing internal polymorphic reference"):
        staging.inspect_bundle(bundle)


def test_internal_logical_target_must_use_id_primary_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding_rows = [
        {
            "id": "plb_1",
            "project_id": "prj_test",
            "entity_type": "manuscript",
            "entity_id": "man_1",
        }
    ]
    target_rows = [{"legacy_id": "man_1", "project_id": "prj_test"}]
    rows = {
        "manuscript_planning_evidence_bindings": binding_rows,
        "manuscripts": target_rows,
    }
    descriptors = {
        "manuscript_planning_evidence_bindings": _simple_descriptor(
            "manuscript_planning_evidence_bindings",
            binding_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
                _column(2, "entity_type", "TEXT"),
                _column(3, "entity_id", "TEXT"),
            ],
        ),
        "manuscripts": _simple_descriptor(
            "manuscripts",
            target_rows,
            [
                _column(0, "legacy_id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
            ],
        ),
    }
    bundle = _write_custom_bundle(tmp_path, monkeypatch, rows, descriptors)

    with pytest.raises(staging.StagingError, match="must use id as its primary key"):
        staging.inspect_bundle(bundle)


@pytest.mark.parametrize(
    ("source_table", "source_row", "target_table"),
    [
        (
            "manuscript_planning_artifact_versions",
            {
                "id": "plv_1",
                "project_id": "prj_test",
                "target_type": "manuscript_claim",
                "target_id": "mcl_missing",
            },
            "manuscript_claims",
        ),
        (
            "manuscript_planning_promotion_events",
            {
                "id": "ppe_1",
                "project_id": "prj_test",
                "promotion_target_type": "manuscript",
                "promotion_target_id": "man_missing",
            },
            "manuscripts",
        ),
        (
            "manuscript_evaluation_events",
            {
                "id": "eva_1",
                "project_id": "prj_test",
                "target_type": "manuscript_reference",
                "target_id": "mrf_missing",
            },
            "manuscript_reference_members",
        ),
        (
            "semantic_patch_context_manifests",
            {
                "id": "pcm_1",
                "project_id": "prj_test",
                "selected_context": '[{"entity_id":"mva_missing"}]',
            },
            "manuscript_claim_verification_attestations",
        ),
    ],
)
def test_internal_logical_references_are_checked_across_every_polymorphic_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_table: str,
    source_row: dict,
    target_table: str,
) -> None:
    source_rows = [source_row]
    target_rows = [{"id": "present_internal_id", "project_id": "prj_test"}]
    rows = {source_table: source_rows, target_table: target_rows}
    source_columns = [
        _column(index, name, "TEXT", pk=1 if name == "id" else 0)
        for index, name in enumerate(source_row)
    ]
    descriptors = {
        source_table: _simple_descriptor(source_table, source_rows, source_columns),
        target_table: _simple_descriptor(
            target_table,
            target_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
            ],
        ),
    }
    bundle = _write_custom_bundle(tmp_path, monkeypatch, rows, descriptors)

    with pytest.raises(staging.StagingError, match="Missing internal polymorphic reference"):
        staging.inspect_bundle(bundle)


def test_non_fk_internal_writer_pointers_are_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_rows = [
        {
            "id": "pla_1",
            "project_id": "prj_test",
            "current_version": 1,
            "current_version_id": "plv_missing",
        }
    ]
    version_rows = [
        {
            "id": "plv_other",
            "artifact_id": "pla_1",
            "project_id": "prj_test",
            "version": 1,
        }
    ]
    rows = {
        "manuscript_planning_artifacts": artifact_rows,
        "manuscript_planning_artifact_versions": version_rows,
    }
    descriptors = {
        "manuscript_planning_artifacts": _simple_descriptor(
            "manuscript_planning_artifacts",
            artifact_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
                _column(2, "current_version", "INTEGER"),
                _column(3, "current_version_id", "TEXT"),
            ],
        ),
        "manuscript_planning_artifact_versions": _simple_descriptor(
            "manuscript_planning_artifact_versions",
            version_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "artifact_id", "TEXT"),
                _column(2, "project_id", "TEXT"),
                _column(3, "version", "INTEGER"),
            ],
        ),
    }
    bundle = _write_custom_bundle(tmp_path, monkeypatch, rows, descriptors)
    with pytest.raises(staging.StagingError, match="current-version reference"):
        staging.inspect_bundle(bundle)

    issue_rows = [
        {
            "id": 1,
            "project_id": "prj_test",
            "attestation_id": "rvd_missing",
        }
    ]
    attestation_rows: list[dict] = []
    rows = {
        "reference_validation_migration_issues": issue_rows,
        "reference_validation_attestations": attestation_rows,
    }
    descriptors = {
        "reference_validation_migration_issues": _simple_descriptor(
            "reference_validation_migration_issues",
            issue_rows,
            [
                _column(0, "id", "INTEGER", pk=1),
                _column(1, "project_id", "TEXT"),
                _column(2, "attestation_id", "TEXT"),
            ],
        ),
        "reference_validation_attestations": _simple_descriptor(
            "reference_validation_attestations",
            attestation_rows,
            [
                _column(0, "id", "TEXT", pk=1),
                _column(1, "project_id", "TEXT"),
            ],
        ),
    }
    bundle = _write_custom_bundle(tmp_path, monkeypatch, rows, descriptors)
    with pytest.raises(staging.StagingError, match="attestation reference"):
        staging.inspect_bundle(bundle)


def test_staged_jsonl_tampering_is_rejected(bundle_factory, tmp_path: Path) -> None:
    bundle, manifest = bundle_factory()
    root = tmp_path / "staging"
    staging.stage_bundle(bundle, root)
    record = (
        root
        / "prj_test"
        / manifest["semantic_root_sha256"]
        / "records"
        / "manuscripts.jsonl"
    )
    record.write_text('{"id":"man_1","legacy_journal_id":"jrn_2","project_id":"prj_test"}\n')
    with pytest.raises(staging.StagingError, match="equivalent"):
        staging.verify_stage(bundle, root)


def test_unknown_bundle_member_is_rejected(bundle_factory) -> None:
    bundle, _ = bundle_factory()
    with zipfile.ZipFile(bundle, "a") as archive:
        archive.writestr("unexpected.txt", b"not part of the contract")
    with pytest.raises(staging.StagingError, match="member inventory mismatch"):
        staging.inspect_bundle(bundle)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("core_references_sha256", "core_references_sha256 mismatch"),
        ("semantic_root_sha256", "semantic_root_sha256 mismatch"),
    ],
)
def test_manifest_digest_drift_is_rejected(bundle_factory, field: str, message: str) -> None:
    bundle, _ = bundle_factory()
    _rewrite_manifest(bundle, lambda manifest: manifest.__setitem__(field, "0" * 64))
    with pytest.raises(staging.StagingError, match=message):
        staging.inspect_bundle(bundle)


def test_primary_key_digest_drift_is_rejected(bundle_factory) -> None:
    bundle, _ = bundle_factory()
    _rewrite_manifest(
        bundle,
        lambda manifest: manifest["tables"]["manuscripts"].__setitem__(
            "primary_key_sha256", "0" * 64
        ),
    )
    with pytest.raises(staging.StagingError, match="Primary-key checksum mismatch"):
        staging.inspect_bundle(bundle)


def test_stage_cli_requires_explicit_staging_root(bundle_factory) -> None:
    bundle, _ = bundle_factory()
    with pytest.raises(SystemExit) as error:
        staging.main(["stage", str(bundle)])
    assert error.value.code == 2
