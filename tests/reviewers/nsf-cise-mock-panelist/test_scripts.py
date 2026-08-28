#!/usr/bin/env python3
"""Regression tests for the deterministic mock-panel utilities."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "nsf-cise-mock-panelist"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from protocol_digest import protocol_bundle_sha256

VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_review.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "nsf_cise_mock_panel_validator", VALIDATOR_PATH
)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
validate_review_module = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = validate_review_module
VALIDATOR_SPEC.loader.exec_module(validate_review_module)
derive_assurance = validate_review_module.derive_assurance

BUILD = SKILL_ROOT / "scripts" / "build_review_packet.py"
BUILD_ARTIFACTS = SKILL_ROOT / "scripts" / "build_artifact_manifest.py"
AGGREGATE = SKILL_ROOT / "scripts" / "aggregate_panel.py"
VALIDATE = SKILL_ROOT / "scripts" / "validate_review.py"
DIMENSIONS = (
    "importance_gap",
    "novelty_transformative",
    "contribution_intellectual_merit",
    "approach_evaluation",
    "feasibility_team_resources",
    "broader_impacts",
    "solicitation_fit",
    "presentation_organization",
    "general_cs_accessibility",
    "writing_precision_professionalism",
    "technical_precision_integrity",
)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class MockPanelScriptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.mock_panel = self.root / "mock-panel"
        self.mock_panel.mkdir()
        self.proposal = self.root / "proposal.md"
        self.proposal.write_text(
            "# Project Description\nA precise gap and method.\n# Broader Impacts\nA measurable plan.\n",
            encoding="utf-8",
        )
        self.authority = self.mock_panel / "authority-snapshot.md"
        self.authority.write_text(
            "# Authority snapshot\nVerified official solicitation and current PAPPG sources.\n",
            encoding="utf-8",
        )
        self.manifest_path = self.mock_panel / "packet-manifest.json"
        result = run_script(
            BUILD,
            "--root",
            str(self.root),
            "--output",
            str(self.manifest_path),
            "--proposal-id",
            "TEST-001",
            "--program",
            "CISE test track",
            "--solicitation-url",
            "https://www.nsf.gov/funding/opportunities/test/solicitation",
            "--policy-verified-on",
            date.today().isoformat(),
            "--classification",
            "proposer-owned",
            "--processing-boundary",
            "Codex workspace; proposer authorized model processing for this fixture.",
            "--external-novelty-search-authorized",
            "--authority",
            str(self.authority),
            "--proposal",
            str(self.proposal),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.input_hashes = {
            record["path"]: record["sha256"] for record in self.manifest["files"]
        }

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def finding(
        self,
        reviewer_id: str,
        suffix: str,
        issue_key: str,
        stance: str,
        severity: str,
        criterion_group: str,
    ) -> dict[str, object]:
        if criterion_group == "presentation":
            audiences = ["general_cs", "adjacent_cise"]
            impacts = ["comprehension", "reviewer_confidence"]
            revision_type = "preserve_or_reinforce" if stance == "strength" else "prose_clarification"
        elif criterion_group == "technical_integrity":
            audiences = ["domain_or_methods_specialist", "all_panelists"]
            impacts = ["scientific_validity", "reviewer_confidence"]
            revision_type = "preserve_or_reinforce" if stance == "strength" else "new_analysis"
        else:
            audiences = ["all_panelists"]
            impacts = ["reviewer_confidence"]
            revision_type = "preserve_or_reinforce" if stance == "strength" else "study_redesign"
        return {
            "id": f"{reviewer_id}-{suffix}",
            "issue_key": issue_key,
            "severity": severity,
            "stance": stance,
            "criterion_group": criterion_group,
            "audiences_affected": audiences,
            "impact_types": impacts,
            "location": "proposal.md, Project Description",
            "claim": f"Test {stance} for {issue_key}.",
            "plain_panel_concern": f"Plain-language panel concern for {issue_key}.",
            "technical_basis": f"Technical basis for {issue_key}.",
            "evidence": [
                {
                    "source": "proposal.md",
                    "location": "Project Description",
                    "note": "Grounded test evidence.",
                }
            ],
            "criterion": "Intellectual Merit or Broader Impacts",
            "rationale": "This changes confidence in the proposal argument.",
            "consequence": "A panelist would adjust the assessment.",
            "action": "Preserve the strength or repair the weakness.",
            "revision_type": revision_type,
            "epistemic_status": "proposal_grounded",
        }

    def review(self, reviewer_id: str, family: str, rating: str) -> dict[str, object]:
        findings = [
            self.finding(reviewer_id, "IM-S01", "importance.precise_gap", "strength", "major", "intellectual_merit"),
            self.finding(reviewer_id, "IM-W01", "evaluation.missing_baseline", "weakness", "major", "intellectual_merit"),
            self.finding(reviewer_id, "BI-S01", "bi.measurable_plan", "strength", "moderate", "broader_impacts"),
            self.finding(reviewer_id, "BI-W01", "bi.sustainability", "weakness", "moderate", "broader_impacts"),
            self.finding(reviewer_id, "WR-S01", "writing.progressive_exposition", "strength", "moderate", "presentation"),
            self.finding(reviewer_id, "TI-S01", "integrity.internal_consistency", "strength", "moderate", "technical_integrity"),
        ]
        dimension_finding = {
            "importance_gap": findings[0]["id"],
            "novelty_transformative": findings[0]["id"],
            "contribution_intellectual_merit": findings[0]["id"],
            "approach_evaluation": findings[1]["id"],
            "feasibility_team_resources": findings[0]["id"],
            "broader_impacts": findings[2]["id"],
            "solicitation_fit": findings[0]["id"],
            "presentation_organization": findings[4]["id"],
            "general_cs_accessibility": findings[4]["id"],
            "writing_precision_professionalism": findings[4]["id"],
            "technical_precision_integrity": findings[5]["id"],
        }
        dimension_map = {
            name: {
                "assessment": "adequate",
                "rationale": f"The evidence for {name} is sufficient for this fixture.",
                "finding_ids": [dimension_finding[name]],
            }
            for name in DIMENSIONS
        }
        profile_map = {
            "R1": ("general_cs", "Broad computer science panelist", "non_specialist"),
            "R2": ("adjacent_cise", "Adjacent CISE systems expert", "adjacent"),
            "R3": ("domain_methods", "Domain and empirical-methods specialist", "specialist"),
        }
        profile_id, background, familiarity = profile_map.get(
            reviewer_id, profile_map["R1"]
        )
        return {
            "schema_version": "1.1",
            "proposal_id": "TEST-001",
            "reviewer_id": reviewer_id,
            "reviewer_role": "holistic mock panelist",
            "reviewer_profile": {
                "profile_id": profile_id,
                "simulated_background": background,
                "domain_familiarity": familiarity,
                "selection_rationale": "Fixture profile selected for complementary panel coverage.",
                "limitations": ["Synthetic test profile; not a real person."],
            },
            "reviewer_route": {
                "route_id": f"fixture-route-{reviewer_id.lower()}",
                "provenance_source": "runtime_metadata",
                "family_basis": "Synthetic runtime metadata used only by the test fixture.",
            },
            "reviewer_model": f"model-{family}",
            "reviewer_family": family,
            "review_independence": "cross-family",
            "conflict_check": {"status": "clear", "notes": "No conflict in fixture."},
            "reviewed_input_hashes": self.input_hashes,
            "rating": {
                "value": rating,
                "scale_source": "public_mock_scale",
                "rationale": "Fixture rationale tied to strengths and weaknesses.",
                "confidence": "medium",
            },
            "summary": "A concise fixture synopsis.",
            "argument_reconstruction": {
                "problem": "The fixture states an important problem.",
                "gap": "The fixture identifies a precise gap.",
                "central_idea": "The fixture proposes a testable central idea.",
                "aims": ["Aim 1 tests the fixture idea."],
                "decisive_tests": ["A matched baseline distinguishes the mechanism."],
                "expected_knowledge": "The fixture yields generalizable knowledge.",
                "first_breakpoint": "No comprehension breakpoint in the synthetic fixture.",
            },
            "intellectual_merit": {
                "strength_finding_ids": [findings[0]["id"]],
                "weakness_finding_ids": [findings[1]["id"]],
            },
            "broader_impacts": {
                "strength_finding_ids": [findings[2]["id"]],
                "weakness_finding_ids": [findings[3]["id"]],
            },
            "writing_and_accessibility": {
                "terminology_notes": "Fixture terminology is stable.",
                "strength_finding_ids": [findings[4]["id"]],
                "weakness_finding_ids": [],
            },
            "technical_precision_integrity": {
                "checks_performed": ["Internal consistency and baseline traceability"],
                "unresolved_checks": [],
                "strength_finding_ids": [findings[5]["id"]],
                "weakness_finding_ids": [],
            },
            "additional_criteria": [],
            "dimensions": dimension_map,
            "findings": findings,
            "questions_for_panel": ["Is the baseline decisive?"],
            "revision_priorities": ["Add the discriminating baseline."],
        }

    def write_reviews(self) -> list[Path]:
        paths: list[Path] = []
        for reviewer_id, family, rating in (
            ("R1", "family-a", "excellent"),
            ("R2", "family-b", "good"),
            ("R3", "family-c", "poor"),
        ):
            path = self.mock_panel / f"review-{reviewer_id.lower()}.json"
            path.write_text(
                json.dumps(self.review(reviewer_id, family, rating), indent=2) + "\n",
                encoding="utf-8",
            )
            paths.append(path)
        return paths

    def panel(self, review_paths: list[Path]) -> dict[str, object]:
        review_hashes = {}
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            review_hashes[review["reviewer_id"]] = sha256_file(path)
        return {
            "schema_version": "1.1",
            "proposal_id": "TEST-001",
            "reviewer_ids": ["R1", "R2", "R3"],
            "chair": {
                "id": "C1",
                "model": "chair-model",
                "family": "family-d",
                "route_id": "fixture-route-chair",
                "provenance_source": "runtime_metadata",
                "family_basis": "Synthetic runtime metadata used only by the fixture.",
            },
            "source_review_hashes": review_hashes,
            "synopsis": "A concise panel synopsis.",
            "mock_disposition": "no_consensus",
            "panel_confidence": "medium",
            "overall_assessment": "The panel retains a material evidence-based disagreement.",
            "intellectual_merit": {
                "strength_finding_ids": ["R1-IM-S01"],
                "weakness_finding_ids": ["R2-IM-W01"],
            },
            "broader_impacts": {
                "strength_finding_ids": ["R1-BI-S01"],
                "weakness_finding_ids": ["R2-BI-W01"],
            },
            "writing_and_accessibility": {
                "assessment": "adequate",
                "synthesis": "The general-CS and adjacent reviewers found the argument navigable.",
                "strength_finding_ids": ["R1-WR-S01"],
                "weakness_finding_ids": [],
            },
            "technical_precision_integrity": {
                "assessment": "adequate",
                "synthesis": "The panel found the synthetic fixture internally consistent.",
                "strength_finding_ids": ["R1-TI-S01"],
                "weakness_finding_ids": [],
            },
            "additional_criteria": [],
            "disagreements": [
                {
                    "topic_key": "overall_rating",
                    "kind": "material_spread",
                    "topic": "overall rating",
                    "positions": {"R1": "excellent", "R2": "good", "R3": "poor"},
                    "evidence": ["proposal.md, Project Description"],
                    "resolution": "Unresolved after checking the fixture.",
                    "minority_view": "R1 remains more positive.",
                }
            ],
            "rating_changes": [],
            "chair_introduced_claims": [],
            "post_chair_verification": {
                "status": "passed",
                "verifier": "meta-01",
                "notes": "All major and chair claims were checked.",
            },
            "conditions_that_would_change_assessment": ["A decisive baseline."],
            "assurance_label": "multi_family_advisory",
            "limitations": "Synthetic fixture; not an NSF decision.",
        }

    def calibration_record(self) -> dict[str, object]:
        return {
            "schema_version": "1.1",
            "profile_id": "fixture-calibration",
            "profile_version": "1.0",
            "skill_profile": {
                "name": "nsf-cise-mock-panelist",
                "protocol_bundle_sha256": protocol_bundle_sha256(SKILL_ROOT),
                "model_families": ["family-a", "family-b", "family-c", "family-d"],
                "model_ids": [
                    "model-family-a",
                    "model-family-b",
                    "model-family-c",
                    "chair-model",
                ],
                "route_topology": "three_independent_reviewers_plus_fresh_chair",
            },
            "evaluated_on": "2026-07-20",
            "calibration_set": {
                "authorized": True,
                "deidentified": True,
                "held_out": True,
                "sample_size": 12,
            },
            "human_anchors": {
                "count": 2,
                "qualification_basis": "Authorized qualified-human fixture anchors.",
                "independent_from_generation": True,
            },
            "metrics": {
                "criterion_coverage": 0.95,
                "finding_precision": 0.8,
                "finding_recall": 0.75,
                "evidence_anchor_accuracy": 0.9,
                "rating_weighted_kappa": 0.65,
                "repeated_run_stability": 0.85,
            },
            "thresholds": {
                "criterion_coverage": 0.9,
                "finding_precision": 0.75,
                "finding_recall": 0.7,
                "evidence_anchor_accuracy": 0.85,
                "rating_weighted_kappa": 0.6,
                "repeated_run_stability": 0.8,
            },
            "result": {
                "status": "passed",
                "thresholds_version": "fixture-thresholds-1",
                "attested_by": "fixture-human-calibration-owner",
                "notes": "Synthetic record used only to test assurance derivation.",
            },
            "limitations": "Synthetic test fixture; not a real calibration claim.",
        }

    def write_ledger(self, review_paths: list[Path]) -> Path:
        proposal_hash = self.input_hashes["proposal.md"]
        ledger_path = self.mock_panel / "issue-ledger.jsonl"
        lines = []
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            for finding in review["findings"]:
                lines.append(
                    json.dumps(
                        {
                            "timestamp": "2026-07-20T18:00:00Z",
                            "proposal_hash": proposal_hash,
                            "actor": review["reviewer_id"],
                            "finding_id": finding["id"],
                            "event": "created",
                            "prior_state": "absent",
                            "new_state": "open",
                            "evidence": [
                                {"source": "proposal.md", "location": "Project Description"}
                            ],
                            "reason": "Frozen individual review created this finding.",
                        },
                        sort_keys=True,
                    )
                )
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return ledger_path

    def prepare_full_run(
        self, review_paths: list[Path]
    ) -> tuple[Path, Path, Path, Path, Path]:
        gate_path = self.mock_panel / "pre-deliberation-validation.json"
        gate_args: list[str] = [
            "--mode",
            "review-gate",
            "--manifest",
            str(self.manifest_path),
        ]
        for path in review_paths:
            gate_args.extend(("--review", str(path)))
        gate = run_script(VALIDATE, *gate_args, "--json-out", str(gate_path))
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        self.assertEqual(json.loads(gate_path.read_text(encoding="utf-8"))["verdict"], "PASS")

        aggregate_path = self.mock_panel / "panel-aggregate.json"
        aggregate_args: list[str] = []
        for path in review_paths:
            aggregate_args.extend(("--review", str(path)))
        aggregate = run_script(
            AGGREGATE,
            *aggregate_args,
            "--minimum-reviews",
            "3",
            "--output",
            str(aggregate_path),
        )
        self.assertEqual(aggregate.returncode, 0, aggregate.stderr)

        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(
            json.dumps(self.panel(review_paths), indent=2) + "\n", encoding="utf-8"
        )
        ledger_path = self.write_ledger(review_paths)
        required_markdown = {
            "compliance-screen.md": "# Compliance\nNo fixture blockers.\n",
            "review-r1.md": "# R1\nFixture review.\n",
            "review-r2.md": "# R2\nFixture review.\n",
            "review-r3.md": "# R3\nFixture review.\n",
            "novelty-audit.md": "# Novelty\nFixture audit.\n",
            "methods-audit.md": "# Methods\nFixture audit.\n",
            "broader-impacts-audit.md": "# Broader Impacts\nFixture audit.\n",
            "presentation-audit.md": "# Presentation\nFixture audit.\n",
            "kill-argument.md": "# Kill argument\nFixture attack.\n",
            "kill-adjudication.md": "# Adjudication\nFixture decision.\n",
            "panel-summary.md": "# Panel summary\nFixture synthesis.\n",
            "review-quality-audit.md": "# Quality audit\nFixture check.\n",
            "revision-priorities.md": "# Priorities\nFixture priority.\n",
        }
        for filename, content in required_markdown.items():
            (self.mock_panel / filename).write_text(content, encoding="utf-8")

        artifact_manifest_path = self.mock_panel / "run-artifact-manifest.json"
        artifact_build = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(artifact_build.returncode, 0, artifact_build.stderr)
        return panel_path, ledger_path, artifact_manifest_path, aggregate_path, gate_path

    def rebuild_artifact_manifest(self, output: Path) -> subprocess.CompletedProcess[str]:
        return run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--output",
            str(output),
        )

    def run_full_validation(
        self,
        review_paths: list[Path],
        panel_path: Path,
        ledger_path: Path,
        artifact_manifest_path: Path,
    ) -> subprocess.CompletedProcess[str]:
        args: list[str] = ["--mode", "full-panel", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        return run_script(
            VALIDATE,
            *args,
            "--panel",
            str(panel_path),
            "--ledger",
            str(ledger_path),
            "--artifact-manifest",
            str(artifact_manifest_path),
        )

    def test_full_clean_pipeline(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, aggregate_path, _ = (
            self.prepare_full_run(review_paths)
        )
        aggregate_json = json.loads(aggregate_path.read_text(encoding="utf-8"))
        self.assertTrue(aggregate_json["disagreements_requiring_chair_review"])
        self.assertEqual(set(aggregate_json["review_hashes"]), {"R1", "R2", "R3"})

        validation_path = self.mock_panel / "validation-report.json"
        validation_args: list[str] = [
            "--mode",
            "full-panel",
            "--manifest",
            str(self.manifest_path),
        ]
        for path in review_paths:
            validation_args.extend(("--review", str(path)))
        validation = run_script(
            VALIDATE,
            *validation_args,
            "--panel",
            str(panel_path),
            "--ledger",
            str(ledger_path),
            "--artifact-manifest",
            str(artifact_manifest_path),
            "--json-out",
            str(validation_path),
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        self.assertEqual(json.loads(validation_path.read_text(encoding="utf-8"))["verdict"], "PASS")

    def test_full_validation_is_review_argument_order_insensitive(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )

        validation = self.run_full_validation(
            list(reversed(review_paths)),
            panel_path,
            ledger_path,
            artifact_manifest_path,
        )

        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_stale_proposal_hash_fails(self) -> None:
        review_path = self.write_reviews()[0]
        self.proposal.write_text("Changed after review.\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("stale hash", validation.stdout)

    def test_validation_report_cannot_overwrite_proposal(self) -> None:
        review_path = self.write_reviews()[0]
        blocked = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
            "--json-out",
            str(self.proposal),
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("cannot overwrite a validated input", blocked.stderr)
        self.assertTrue(self.proposal.read_text(encoding="utf-8").startswith("# Project Description"))

    def test_official_nsf_review_material_is_rejected_before_manifest(self) -> None:
        blocked = run_script(
            BUILD,
            "--root",
            str(self.root),
            "--output",
            str(self.root / "blocked.json"),
            "--proposal-id",
            "BLOCKED",
            "--classification",
            "official-nsf-review-material",
            "--processing-boundary",
            "Blocked fixture boundary.",
            "--proposal",
            str(self.proposal),
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("do not process", blocked.stderr)
        self.assertFalse((self.root / "blocked.json").exists())

    def test_minimum_review_count_is_enforced(self) -> None:
        review_path = self.write_reviews()[0]
        validation = run_script(
            VALIDATE,
            "--mode",
            "review-gate",
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("at least 3 required", validation.stdout)

    def test_review_gate_requires_one_of_each_reviewer_profile(self) -> None:
        review_paths = self.write_reviews()
        duplicate = json.loads(review_paths[2].read_text(encoding="utf-8"))
        duplicate["reviewer_profile"] = dict(
            json.loads(review_paths[0].read_text(encoding="utf-8"))["reviewer_profile"]
        )
        review_paths[2].write_text(json.dumps(duplicate, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--mode", "review-gate", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args)
        self.assertEqual(validation.returncode, 1)
        self.assertIn("exactly one reviewer profile each", validation.stdout)

    def test_review_gate_requires_distinct_simulated_backgrounds(self) -> None:
        review_paths = self.write_reviews()
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            review["reviewer_profile"]["simulated_background"] = "Identical generic background"
            path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--mode", "review-gate", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args)
        self.assertEqual(validation.returncode, 1)
        self.assertIn("three distinct simulated backgrounds", validation.stdout)

    def test_reviewer_profile_familiarity_must_match_profile(self) -> None:
        review = self.review("R1", "family-a", "good")
        review["reviewer_profile"]["domain_familiarity"] = "specialist"
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("requires domain_familiarity 'non_specialist'", validation.stdout)

    def test_same_model_cannot_claim_multiple_model_families(self) -> None:
        review_paths = self.write_reviews()
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            review["reviewer_model"] = "identical-model"
            path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--mode", "review-gate", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args)
        self.assertEqual(validation.returncode, 1)
        self.assertIn("maps to multiple families", validation.stdout)

    def test_self_reported_routes_cannot_earn_multi_family_assurance(self) -> None:
        review_paths = self.write_reviews()
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            review["reviewer_route"]["provenance_source"] = "self_reported"
            path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--mode", "review-gate", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args)
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        report = json.loads(validation.stdout)
        self.assertEqual(report["derived_assurance"], "provisional_advisory")
        self.assertEqual(report["verdict"], "WARN")

    def test_human_calibration_cannot_override_untrusted_route_topology(self) -> None:
        reviews = [
            self.review("R1", "family-a", "good"),
            self.review("R2", "family-b", "good"),
            self.review("R3", "family-c", "good"),
        ]
        for review in reviews:
            review["reviewer_route"]["provenance_source"] = "self_reported"
            review["review_independence"] = "single-context"
        self.assertEqual(
            derive_assurance(
                reviews,
                human_calibration_passed=True,
                chair_route_trusted=True,
            ),
            "provisional_advisory",
        )

    def test_review_gate_requires_distinct_route_ids(self) -> None:
        review_paths = self.write_reviews()
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            review["reviewer_route"]["route_id"] = "same-route"
            path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--mode", "review-gate", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args)
        self.assertEqual(validation.returncode, 1)
        self.assertIn("three distinct reviewer route IDs", validation.stdout)

    def test_review_requires_writing_or_accessibility_evidence(self) -> None:
        review = self.review("R1", "family-a", "good")
        review["writing_and_accessibility"]["strength_finding_ids"] = []
        review["writing_and_accessibility"]["weakness_finding_ids"] = []
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("must cite at least one strength or weakness finding", validation.stdout)

    def test_accessibility_dimension_rejects_intellectual_merit_finding(self) -> None:
        review = self.review("R1", "family-a", "good")
        review["dimensions"]["general_cs_accessibility"]["finding_ids"] = ["R1-IM-S01"]
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("general_cs_accessibility", validation.stdout)
        self.assertIn("wrong criterion_group", validation.stdout)

    def test_accessibility_evidence_must_affect_general_cs_audience(self) -> None:
        review = self.review("R1", "family-a", "good")
        writing_finding = next(
            finding
            for finding in review["findings"]
            if finding["id"] == "R1-WR-S01"
        )
        writing_finding["audiences_affected"] = ["domain_or_methods_specialist"]
        writing_finding["impact_types"] = ["scientific_validity"]
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("lacks audience-appropriate evidence", validation.stdout)

    def test_weak_dimension_requires_weakness_support(self) -> None:
        review = self.review("R1", "family-a", "good")
        review["dimensions"]["general_cs_accessibility"]["assessment"] = "weak"
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("weak assessment requires a linked weakness finding", validation.stdout)

    def test_packet_output_cannot_overwrite_proposal(self) -> None:
        blocked = run_script(
            BUILD,
            "--root",
            str(self.root),
            "--output",
            str(self.proposal),
            "--proposal-id",
            "ALIAS",
            "--classification",
            "proposer-owned",
            "--processing-boundary",
            "Codex workspace fixture.",
            "--proposal",
            str(self.proposal),
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("aliases a pinned input", blocked.stderr)
        self.assertTrue(self.proposal.read_text(encoding="utf-8").startswith("# Project Description"))

    def test_aggregate_output_cannot_overwrite_frozen_review(self) -> None:
        review_path = self.write_reviews()[0]
        blocked = run_script(
            AGGREGATE,
            "--review",
            str(review_path),
            "--output",
            str(review_path),
        )
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("cannot overwrite a frozen review", blocked.stderr)
        restored = json.loads(review_path.read_text(encoding="utf-8"))
        self.assertEqual(restored["reviewer_id"], "R1")

    def test_json_schema_rejects_unexpected_properties(self) -> None:
        review = self.review("R1", "family-a", "good")
        review["unexpected_top_level"] = True
        review["findings"][0]["unexpected_finding_field"] = "bad"
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("unexpected property", validation.stdout)

    def test_non_adjacent_split_rating_is_rejected(self) -> None:
        review = self.review("R1", "family-a", "excellent")
        review["rating"]["adjacent_split"] = "poor"
        review_path = self.mock_panel / "review-r1.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        validation = run_script(
            VALIDATE,
            "--manifest",
            str(self.manifest_path),
            "--review",
            str(review_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("adjacent_split must be exactly one rating band away", validation.stdout)

    def test_chair_cannot_self_declare_human_calibration(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        panel["assurance_label"] = "human_calibrated_advisory"
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("assurance_label is self-inconsistent", validation.stdout)

    def test_full_panel_requires_post_chair_verification(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        panel["post_chair_verification"]["status"] = "not_run"
        panel["post_chair_verification"]["notes"] = "Deliberately omitted in fixture."
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        rebuilt = self.rebuild_artifact_manifest(artifact_manifest_path)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("post-chair verification was not run", validation.stdout)

    def test_panel_must_synthesize_nonempty_im_and_bi(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        panel["intellectual_merit"] = {
            "strength_finding_ids": [],
            "weakness_finding_ids": [],
        }
        panel["broader_impacts"] = {
            "strength_finding_ids": [],
            "weakness_finding_ids": [],
        }
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("requires at least 1 items", validation.stdout)

    def test_panel_must_synthesize_writing_and_technical_integrity(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        del panel["writing_and_accessibility"]
        del panel["technical_precision_integrity"]
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("missing required property 'writing_and_accessibility'", validation.stdout)
        self.assertIn("missing required property 'technical_precision_integrity'", validation.stdout)

    def test_panel_weak_coverage_requires_weakness_support(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        panel["writing_and_accessibility"]["assessment"] = "weak"
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("weak assessment requires a linked weakness finding", validation.stdout)

    def test_panel_cannot_suppress_mechanically_flagged_disagreement(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        panel["disagreements"] = []
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("omit mechanically flagged topics", validation.stdout)

    def test_chair_route_must_be_distinct_from_reviewers(self) -> None:
        review_paths = self.write_reviews()
        panel = self.panel(review_paths)
        panel["chair"]["route_id"] = "fixture-route-r1"
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("chair route_id must be distinct", validation.stdout)

    def test_protocol_digest_changes_with_behavior_file(self) -> None:
        protocol_root = self.root / "protocol-fixture"
        protocol_root.mkdir()
        (protocol_root / "SKILL.md").write_text("# Fixture\n", encoding="utf-8")
        for directory in ("agents", "assets", "references", "scripts"):
            (protocol_root / directory).mkdir()
        behavior_file = protocol_root / "references" / "rubric.md"
        behavior_file.write_text("version one\n", encoding="utf-8")
        first = protocol_bundle_sha256(protocol_root)
        behavior_file.write_text("version two\n", encoding="utf-8")
        second = protocol_bundle_sha256(protocol_root)
        self.assertNotEqual(first, second)

    def test_panel_cannot_omit_additional_criteria_from_reviews(self) -> None:
        review_paths = self.write_reviews()
        for path in review_paths:
            review = json.loads(path.read_text(encoding="utf-8"))
            reviewer_id = review["reviewer_id"]
            strength = self.finding(
                reviewer_id,
                "ADD-S01",
                "track.relevance",
                "strength",
                "moderate",
                "additional_criterion",
            )
            weakness = self.finding(
                reviewer_id,
                "ADD-W01",
                "track.validation",
                "weakness",
                "moderate",
                "additional_criterion",
            )
            review["findings"].extend((strength, weakness))
            review["additional_criteria"] = [
                {
                    "criterion": "Fixture track criterion",
                    "source": "Official fixture solicitation, section VI",
                    "strength_finding_ids": [strength["id"]],
                    "weakness_finding_ids": [weakness["id"]],
                }
            ]
            path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        panel_path = self.mock_panel / "panel-summary.json"
        panel_path.write_text(
            json.dumps(self.panel(review_paths), indent=2) + "\n", encoding="utf-8"
        )
        args: list[str] = ["--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(VALIDATE, *args, "--panel", str(panel_path))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("panel additional criteria do not match sealed reviews", validation.stdout)

    def test_full_panel_rederives_aggregate_from_frozen_reviews(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, aggregate_path, _ = (
            self.prepare_full_run(review_paths)
        )
        aggregate_path.write_text("{}\n", encoding="utf-8")
        rebuilt = self.rebuild_artifact_manifest(artifact_manifest_path)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("panel aggregate does not exactly match", validation.stdout)

    def test_full_validation_is_independent_of_review_argument_order(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        validation = self.run_full_validation(
            list(reversed(review_paths)),
            panel_path,
            ledger_path,
            artifact_manifest_path,
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_rating_change_ledger_states_must_match_panel(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        panel["rating_changes"] = [
            {
                "reviewer_id": "R1",
                "initial": "excellent",
                "revised": "very_good",
                "trigger": "Bounded deliberation evidence.",
                "evidence": ["proposal.md, Project Description"],
                "rationale": "The evidence lowered the final assessment by one band.",
            }
        ]
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        mismatch_event = {
            "timestamp": "2026-07-20T18:01:00Z",
            "proposal_hash": self.input_hashes["proposal.md"],
            "actor": "R1",
            "finding_id": "rating:R1",
            "event": "rating_changed",
            "prior_state": "good",
            "new_state": "fair",
            "evidence": [{"source": "proposal.md", "location": "Project Description"}],
            "reason": "Deliberation event deliberately contradicts the panel fixture.",
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(mismatch_event, sort_keys=True) + "\n")
        rebuilt = self.rebuild_artifact_manifest(artifact_manifest_path)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("rating_changed ledger states do not match panel", validation.stdout)

    def test_not_comparable_is_a_valid_revision_ledger_outcome(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        event = {
            "timestamp": "2026-07-20T18:01:00Z",
            "proposal_hash": self.input_hashes["proposal.md"],
            "actor": "revision-adjudicator",
            "finding_id": "R1-IM-W01",
            "event": "not_comparable",
            "prior_state": "open",
            "new_state": "not_comparable",
            "evidence": [{"source": "proposal.md", "location": "Project Description"}],
            "reason": "The fixture versions do not expose comparable evidence.",
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        rebuilt = self.rebuild_artifact_manifest(artifact_manifest_path)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_chair_claim_ledger_status_must_match_panel(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        panel["chair_introduced_claims"] = [
            {
                "id": "C1-CLAIM-01",
                "claim": "A chair-introduced fixture claim.",
                "evidence": ["proposal.md, Project Description"],
                "verification_status": "verified",
            }
        ]
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        mismatch_event = {
            "timestamp": "2026-07-20T18:01:00Z",
            "proposal_hash": self.input_hashes["proposal.md"],
            "actor": "meta-01",
            "finding_id": "C1-CLAIM-01",
            "event": "chair_claim_verified",
            "prior_state": "unverified",
            "new_state": "qualified",
            "evidence": [{"source": "proposal.md", "location": "Project Description"}],
            "reason": "The ledger deliberately disagrees with the panel fixture.",
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(mismatch_event, sort_keys=True) + "\n")
        rebuilt = self.rebuild_artifact_manifest(artifact_manifest_path)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("chair claim ledger status does not match panel", validation.stdout)

    def test_pre_deliberation_gate_is_bound_to_exact_review_hashes(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        revised = json.loads(review_paths[0].read_text(encoding="utf-8"))
        revised["summary"] = "A changed but still schema-valid review after the gate."
        review_paths[0].write_text(json.dumps(revised, indent=2) + "\n", encoding="utf-8")
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        panel["source_review_hashes"]["R1"] = sha256_file(review_paths[0])
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        args: list[str] = ["--mode", "full-panel", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(
            VALIDATE,
            *args,
            "--panel",
            str(panel_path),
            "--ledger",
            str(ledger_path),
            "--artifact-manifest",
            str(artifact_manifest_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("pre-deliberation gate review hashes do not match", validation.stdout)

    def test_unknown_ledger_finding_is_rejected(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        unknown_event = {
            "timestamp": "2026-07-20T18:01:00Z",
            "proposal_hash": self.input_hashes["proposal.md"],
            "actor": "chair-01",
            "finding_id": "UNKNOWN-W01",
            "event": "created",
            "prior_state": "absent",
            "new_state": "open",
            "evidence": [{"source": "proposal.md", "location": "Project Description"}],
            "reason": "This unknown ID must not enter the audit trail.",
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(unknown_event, sort_keys=True) + "\n")
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        args: list[str] = ["--mode", "full-panel", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(
            VALIDATE,
            *args,
            "--panel",
            str(panel_path),
            "--ledger",
            str(ledger_path),
            "--artifact-manifest",
            str(artifact_manifest_path),
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("unknown finding_id 'UNKNOWN-W01'", validation.stdout)

    def test_invalid_human_calibration_record_is_rejected(self) -> None:
        review_paths = self.write_reviews()
        _, _, artifact_manifest_path, _, _ = self.prepare_full_run(review_paths)
        calibration_path = self.mock_panel / "human-calibration-record.json"
        calibration_path.write_text("{}\n", encoding="utf-8")
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--human-calibration-record",
            str(calibration_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 2)
        self.assertIn("invalid human calibration record", rebuilt.stderr)

    def test_human_calibration_set_must_be_deidentified(self) -> None:
        review_paths = self.write_reviews()
        _, _, artifact_manifest_path, _, _ = self.prepare_full_run(review_paths)
        calibration = self.calibration_record()
        calibration["calibration_set"]["deidentified"] = False
        calibration_path = self.mock_panel / "human-calibration-record.json"
        calibration_path.write_text(
            json.dumps(calibration, indent=2) + "\n", encoding="utf-8"
        )
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--human-calibration-record",
            str(calibration_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 2)
        self.assertIn("must equal True", rebuilt.stderr)

    def test_human_calibration_requires_exact_model_identifiers(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        calibration = self.calibration_record()
        calibration["skill_profile"]["model_ids"].remove("chair-model")
        calibration_path = self.mock_panel / "human-calibration-record.json"
        calibration_path.write_text(
            json.dumps(calibration, indent=2) + "\n", encoding="utf-8"
        )
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--human-calibration-record",
            str(calibration_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        validation = self.run_full_validation(
            review_paths, panel_path, ledger_path, artifact_manifest_path
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("does not cover model identifiers: chair-model", validation.stdout)

    def test_valid_human_calibration_record_controls_assurance(self) -> None:
        review_paths = self.write_reviews()
        panel_path, ledger_path, artifact_manifest_path, _, _ = self.prepare_full_run(
            review_paths
        )
        calibration = self.calibration_record()
        calibration_path = self.mock_panel / "human-calibration-record.json"
        calibration_path.write_text(
            json.dumps(calibration, indent=2) + "\n", encoding="utf-8"
        )
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        panel["assurance_label"] = "human_calibrated_advisory"
        panel_path.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
        rebuilt = run_script(
            BUILD_ARTIFACTS,
            "--artifact-dir",
            str(self.mock_panel),
            "--packet",
            str(self.manifest_path),
            "--human-calibration-record",
            str(calibration_path),
            "--output",
            str(artifact_manifest_path),
        )
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        args: list[str] = ["--mode", "full-panel", "--manifest", str(self.manifest_path)]
        for path in review_paths:
            args.extend(("--review", str(path)))
        validation = run_script(
            VALIDATE,
            *args,
            "--panel",
            str(panel_path),
            "--ledger",
            str(ledger_path),
            "--artifact-manifest",
            str(artifact_manifest_path),
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        report = json.loads(validation.stdout)
        self.assertEqual(report["derived_assurance"], "human_calibrated_advisory")


if __name__ == "__main__":
    unittest.main()
