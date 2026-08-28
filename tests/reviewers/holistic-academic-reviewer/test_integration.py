from __future__ import annotations

import copy
import contextlib
import io
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills"
SKILL_ROOT = SKILLS_ROOT / "holistic-academic-reviewer"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "validate_academic_review.py"
SCHEMA_PATH = SKILL_ROOT / "schemas" / "academic-session-envelope.schema.json"
MANIFEST_PATH = SKILL_ROOT / "assets" / "engine-manifest.json"

SPEC = importlib.util.spec_from_file_location("validate_academic_review", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


def write_bytes(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return runtime.sha256_file(path)


def collect_property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(str(key) for key in properties)
        for child in value.values():
            names.update(collect_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(collect_property_names(child))
    return names


class AcademicReviewerIntegrationTests(unittest.TestCase):
    maxDiff = None

    def make_session(self, directory: Path, artifact_kind: str = "research_paper") -> dict[str, Any]:
        input_hash = write_bytes(directory / "inputs" / "primary.pdf", b"review input\n")
        if artifact_kind == "research_paper":
            engine_id = "ai-cyber-paper-reviewer"
            authority_profile = "venue_profile"
            output_role = "paper_review_bundle"
            validator = "ai-cyber-paper-reviewer/scripts/validate_review.py"
            output_path = directory / "native" / "paper-review.json"
        else:
            engine_id = "nsf-cise-mock-panelist"
            authority_profile = "nsf_solicitation_profile"
            output_role = "nsf_cise_panel_summary"
            validator = "nsf-cise-mock-panelist/scripts/validate_review.py"
            output_path = directory / "native" / "panel-summary.json"
        output_hash = write_bytes(output_path, b"{}\n")
        return {
            "schema_version": "1.0.0",
            "session_id": "session-001",
            "created_at": "2026-07-22T18:00:00Z",
            "artifact_kind": artifact_kind,
            "engine_id": engine_id,
            "privacy_mode": "local_only",
            "authority": {
                "profile": authority_profile,
                "status": "unknown",
                "snapshot_output_id": None,
            },
            "engine_manifest_sha256": runtime.sha256_file(MANIFEST_PATH),
            "input_artifacts": [
                {
                    "artifact_id": "A-primary",
                    "role": "primary",
                    "path": "inputs/primary.pdf",
                    "sha256": input_hash,
                    "media_type": "application/pdf",
                    "inspection_status": "complete",
                }
            ],
            "native_outputs": [
                {
                    "output_id": "O-native",
                    "native_role": output_role,
                    "path": output_path.relative_to(directory).as_posix(),
                    "sha256": output_hash,
                    "media_type": "application/json",
                }
            ],
            "native_validation": {
                "status": "not_run",
                "validator": validator,
                "validator_exit_code": None,
                "validated_at": None,
                "report_output_id": None,
            },
            "limitations": [],
        }

    def make_fake_skill_root(self, directory: Path) -> Path:
        for engine_id, engine_spec in runtime.ENGINE_SPECS.items():
            engine_root = directory / engine_spec["root"]
            write_bytes(engine_root / "SKILL.md", f"engine {engine_id}\n".encode())
            write_bytes(directory / engine_spec["validator"], b"#!/usr/bin/env python3\n")
        manifest = runtime.build_manifest_data(directory)
        manifest_path = directory / "holistic-academic-reviewer" / "assets" / "engine-manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest_path

    def test_packaged_engine_manifest_matches_native_files(self) -> None:
        self.assertEqual(runtime.verify_engine_manifest(), [])
        manifest = json.loads(MANIFEST_PATH.read_text())
        self.assertEqual(
            [engine["id"] for engine in manifest["engines"]],
            sorted(runtime.ENGINE_SPECS),
        )
        self.assertNotIn(str(SKILL_ROOT), MANIFEST_PATH.read_text())

    def test_manifest_integrity_detects_engine_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.make_fake_skill_root(root)
            self.assertEqual(runtime.verify_engine_manifest(root, manifest_path), [])
            target = root / "ai-cyber-paper-reviewer" / "SKILL.md"
            target.write_text("tampered\n")
            errors = runtime.verify_engine_manifest(root, manifest_path)
            self.assertTrue(any("failed integrity verification" in error for error in errors), errors)

    def test_manifest_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.make_fake_skill_root(root)
            manifest = json.loads(manifest_path.read_text())
            manifest["engines"][0]["files"][0]["path"] = "../escape"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            errors = runtime.verify_engine_manifest(root, manifest_path)
            self.assertTrue(any("traversal" in error for error in errors), errors)

    def test_manifest_detects_untracked_hidden_engine_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.make_fake_skill_root(root)
            hidden = root / "ai-cyber-paper-reviewer" / ".untracked-payload.md"
            hidden.write_text("untracked\n")
            errors = runtime.verify_engine_manifest(root, manifest_path)
            self.assertTrue(any("not manifested" in error for error in errors), errors)

    def test_malformed_manifest_records_return_errors_without_crashing(self) -> None:
        mutations = {
            "missing path": lambda record: record.pop("path"),
            "non-ascii hash": lambda record: record.__setitem__("sha256", "é"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                manifest_path = self.make_fake_skill_root(root)
                manifest = json.loads(manifest_path.read_text())
                mutate(manifest["engines"][0]["files"][0])
                manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
                errors = runtime.verify_engine_manifest(root, manifest_path)
                self.assertTrue(errors)
                self.assertTrue(any("malformed file records" in error for error in errors), errors)

    def test_both_allowed_artifact_kinds_validate(self) -> None:
        for artifact_kind in sorted(runtime.ARTIFACT_KINDS):
            with self.subTest(artifact_kind=artifact_kind), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                session = self.make_session(directory, artifact_kind)
                errors = runtime.validate_session_data(session, directory / "session.json")
                self.assertEqual(errors, [])

    def test_unrecognized_artifact_kind_and_cross_engine_pairing_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            session = self.make_session(directory)
            session["artifact_kind"] = "generic_academic_document"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("unsupported artifact kind" in error for error in errors), errors)

            session = self.make_session(directory)
            session["engine_id"] = "nsf-cise-mock-panelist"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("do not match" in error for error in errors), errors)

    def test_native_output_roles_cannot_cross_engines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            session = self.make_session(directory)
            session["native_outputs"][0]["native_role"] = "nsf_cise_panel_summary"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("different or unknown engine" in error for error in errors), errors)

    def test_envelope_rejects_universal_judgment_fields(self) -> None:
        forbidden = {"score", "rating", "recommendation", "disposition", "confidence", "assurance"}
        schema = json.loads(SCHEMA_PATH.read_text())
        self.assertTrue(forbidden.isdisjoint(collect_property_names(schema)))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for field in sorted(forbidden):
                with self.subTest(field=field):
                    session = self.make_session(directory)
                    session[field] = "forbidden"
                    errors = runtime.validate_session_data(session, directory / "session.json")
                    self.assertTrue(any(field in error for error in errors), errors)

            session = self.make_session(directory)
            session["native_outputs"][0]["score"] = 0.9
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("score" in error for error in errors), errors)

    def test_session_paths_are_relative_contained_and_nonoverwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            session = self.make_session(directory)
            session["native_outputs"][0]["path"] = "../outside.json"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("traversal" in error for error in errors), errors)

            session = self.make_session(directory)
            session["native_outputs"][0]["path"] = session["input_artifacts"][0]["path"]
            session["native_outputs"][0]["sha256"] = session["input_artifacts"][0]["sha256"]
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("must not overwrite" in error for error in errors), errors)

    def test_session_rejects_symlink_and_hardlink_output_aliases(self) -> None:
        for alias_kind in ("symlink", "hardlink"):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                session = self.make_session(directory)
                input_path = directory / session["input_artifacts"][0]["path"]
                output_path = directory / session["native_outputs"][0]["path"]
                output_path.unlink()
                if alias_kind == "symlink":
                    output_path.symlink_to(input_path)
                else:
                    output_path.hardlink_to(input_path)
                session["native_outputs"][0]["sha256"] = session["input_artifacts"][0]["sha256"]
                errors = runtime.validate_session_data(session, directory / "session.json")
                expected = "symbolic-link" if alias_kind == "symlink" else "aliases an input"
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_session_rejects_control_character_path_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            session = self.make_session(directory)
            session["native_outputs"][0]["path"] = "native/\u0000bad.json"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("control characters" in error for error in errors), errors)

    def test_schema_and_runtime_reject_non_normalized_paths(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        pattern = re.compile(schema["$defs"]["relativePath"]["pattern"])
        for bad_path in ("inputs//primary.pdf", "inputs/", "native/\u0000bad.json"):
            with self.subTest(path=bad_path):
                self.assertIsNone(pattern.fullmatch(bad_path))
                errors: list[str] = []
                self.assertIsNone(runtime._safe_relative_path(bad_path, "path", errors))
                self.assertTrue(errors)

    def test_verified_authority_and_completed_validation_require_linked_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            session = self.make_session(directory)
            session["authority"]["status"] = "verified"
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("verified authority requires" in error for error in errors), errors)

            session = self.make_session(directory)
            session["native_validation"].update(
                {
                    "status": "passed",
                    "validator_exit_code": 0,
                    "validated_at": "2026-07-22T18:01:00Z",
                    "report_output_id": None,
                }
            )
            errors = runtime.validate_session_data(session, directory / "session.json")
            self.assertTrue(any("completed validation requires" in error for error in errors), errors)

    def test_list_cli_has_no_argument_forwarding_or_manifest_write(self) -> None:
        listed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), "list-engines", "--json"],
            cwd=SKILL_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(listed.returncode, 0, listed.stderr)
        payload = json.loads(listed.stdout)
        self.assertEqual(
            [engine["id"] for engine in payload["engines"]],
            sorted(runtime.ENGINE_SPECS),
        )
        help_result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), "--help"],
            cwd=SKILL_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertNotIn("dispatch", help_result.stdout)
        self.assertNotIn("build-manifest", help_result.stdout)

    def test_verify_cli_failure_does_not_claim_manifest_is_valid(self) -> None:
        output = io.StringIO()
        with mock.patch.object(
            runtime,
            "verify_engine_manifest",
            return_value=["engine bundle failed integrity verification"],
        ), contextlib.redirect_stdout(output):
            return_code = runtime.main(["verify-engines", "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(return_code, 1)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["message"], "engine manifest validation failed")
        self.assertNotIn("are valid", payload["message"])

    def test_session_cli_failure_does_not_claim_session_is_valid(self) -> None:
        output = io.StringIO()
        with mock.patch.object(
            runtime,
            "validate_session_file",
            return_value=["session is invalid"],
        ), contextlib.redirect_stdout(output):
            return_code = runtime.main(
                ["validate-session", "invalid-session.json", "--json"]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(return_code, 1)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["message"], "academic session validation failed")
        self.assertNotIn("are valid", payload["message"])

    def test_schema_and_runtime_contracts_do_not_drift(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        self.assertEqual(set(schema["properties"]["artifact_kind"]["enum"]), runtime.ARTIFACT_KINDS)
        self.assertEqual(set(schema["properties"]["engine_id"]["enum"]), set(runtime.ENGINE_SPECS))
        self.assertEqual(
            set(schema["properties"]["privacy_mode"]["enum"]), runtime.PRIVACY_MODES
        )
        paper_roles = set(schema["$defs"]["paperNativeRole"]["enum"])
        proposal_roles = set(schema["$defs"]["nsfNativeRole"]["enum"])
        self.assertEqual(
            paper_roles,
            runtime.ENGINE_SPECS["ai-cyber-paper-reviewer"]["native_roles"],
        )
        self.assertEqual(
            proposal_roles,
            runtime.ENGINE_SPECS["nsf-cise-mock-panelist"]["native_roles"],
        )
        self.assertTrue(paper_roles.isdisjoint(proposal_roles))


if __name__ == "__main__":
    unittest.main()
