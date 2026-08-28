#!/usr/bin/env python3
"""Regression tests for the deterministic review-bundle validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Sequence, Union


REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = REPO_ROOT / "skills" / "ai-cyber-paper-reviewer"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
VALIDATOR_PATH = ROOT / "scripts" / "validate_review.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "ai_cyber_paper_review_validator", VALIDATOR_PATH
)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
validate_review = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = validate_review
VALIDATOR_SPEC.loader.exec_module(validate_review)


PathPart = Union[str, int]


def load_json(name: str) -> Any:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parent_at(document: Any, path: Sequence[PathPart]) -> tuple[Any, PathPart]:
    if not path:
        raise ValueError("mutation path must not be empty")
    current = document
    for part in path[:-1]:
        current = current[part]
    return current, path[-1]


def apply_case(bundle: Dict[str, Any], case: Dict[str, Any]) -> None:
    operation = case["operation"]
    if operation == "duplicate_finding":
        bundle["findings"].append(copy.deepcopy(bundle["findings"][case["finding_index"]]))
        return
    if operation == "remove":
        parent, key = parent_at(bundle, case["path"])
        del parent[key]
        return
    if operation == "set":
        parent, key = parent_at(bundle, case["path"])
        parent[key] = case["value"]
        return
    if operation == "set_many":
        for change in case["changes"]:
            parent, key = parent_at(bundle, change["path"])
            parent[key] = change["value"]
        return
    raise ValueError(f"unsupported fixture operation: {operation}")


class ReviewBundleValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_bundle = load_json("valid_bundle.json")
        self.valid_interaction = load_json("valid_interaction_log.json")
        self.detached_initial_digest = self.valid_interaction[
            "initial_review_snapshot"
        ]["review_sha256"]
        self.negative_cases = load_json("negative_cases.json")

    def issue_codes(self, bundle: Dict[str, Any]) -> List[str]:
        detached_digest = (
            self.detached_initial_digest if "interaction_log" in bundle else None
        )
        return [
            issue.code
            for issue in validate_review.validate_bundle(
                bundle,
                trusted_initial_review_sha256=detached_digest,
            )
        ]

    def attach_valid_interaction(self) -> None:
        self.valid_bundle["mode"] = "interactive"
        self.valid_bundle["interaction_log"] = copy.deepcopy(self.valid_interaction)

    def refresh_detached_initial_digest(self) -> None:
        snapshot = self.valid_bundle["interaction_log"]["initial_review_snapshot"]
        digest = validate_review.canonical_initial_review_sha256(
            self.valid_bundle, snapshot["initial_mode"]
        )
        snapshot["review_sha256"] = digest
        self.detached_initial_digest = digest

    def attach_valid_post_freeze_finding(self, severity: str = "major") -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["evidence_artifacts"] = [
            {
                "id": "E-PF-001",
                "kind": "author_response_text",
                "label": "Hashed response text that revealed a new concern",
                "sha256": "7" * 64,
                "supplied_at": "2026-07-22T17:00:00-04:00",
                "external_disclosure_limit": "local_only",
                "confidentiality_restrictions": "Keep within the authorized chat runtime.",
            }
        ]
        log["author_responses"][0]["new_evidence_artifact_ids"] = ["E-PF-001"]
        verifier_id = None
        verification_status = "not_required"
        verified_severity = None
        checked_evidence = False
        verification_performed_at = None
        verification_report_sha256 = None
        if severity == "critical":
            self.valid_bundle["reviewers"][1]["role"] = "critical_verifier"
            verifier_id = "R-SECURITY"
            verification_status = "confirmed"
            verified_severity = "critical"
            checked_evidence = True
            verification_performed_at = "2026-07-22T17:20:00-04:00"
            verification_report_sha256 = "9" * 64
        log["post_freeze_findings"] = [
            {
                "id": "PF-001",
                "origin": {
                    "label": "new_in_rebuttal",
                    "round": 1,
                    "question_id": "Q-001",
                },
                "reviewer_id": "R-GENERAL",
                "verifier_id": verifier_id,
                "verification_status": verification_status,
                "verified_severity": verified_severity,
                "checked_evidence": checked_evidence,
                "verification_performed_at": verification_performed_at,
                "verification_report_sha256": verification_report_sha256,
                "verification_rationale": "The linked response evidence was checked under the stated verification level.",
                "category": "claims_motivation",
                "severity": severity,
                "confidence": 0.83,
                "conditional": False,
                "status": "open",
                "observation": "The answer introduces a new central claim not visible in the frozen submission.",
                "rationale_not_in_initial_review": "The central claim first appeared in the author's actual response and could not have been inferred from the frozen manuscript.",
                "evidence_artifact_ids": ["E-PF-001"],
                "linked_initial_finding_ids": ["F-001"],
            }
        ]
        meta = log["revised_provisional_meta_review"]
        meta["post_freeze_finding_treatments"] = [
            {
                "finding_id": "PF-001",
                "treatment": "affects_provisional_recommendation",
                "rationale": "The newly revealed central claim is material to the provisional assessment.",
            }
        ]
        meta["new_evidence_dependency_ids"] = ["E-PF-001"]
        if severity == "critical":
            self.refresh_detached_initial_digest()

    def set_valid_venue_rebuttal_rules(self) -> None:
        log = self.valid_bundle["interaction_log"]
        log["interaction_type"] = "venue_rebuttal_simulation"
        log["venue_rebuttal_rules"] = {
            "venue": "Example Security Conference",
            "year": 2026,
            "track": "Research",
            "paper_type": "Full paper",
            "stage": "Author response",
            "verified_at": "2026-07-22T16:31:00-04:00",
            "official_source_locators": [
                "https://example.org/official-response-rules"
            ],
            "external_check_ids": [],
            "length_rule": "Maximum 500 words.",
            "scope_rule": "Address reviewer questions and factual errors only.",
            "link_rule": "No new external links.",
            "anonymity_rule": "Preserve double-blind anonymity.",
            "new_evidence_rule": "No new experiments.",
            "round_rule": "One author-response round.",
        }

    def test_valid_bundle_passes(self) -> None:
        self.assertEqual(validate_review.validate_bundle(self.valid_bundle), [])

    def test_duplicate_finding_ids_fail(self) -> None:
        case = self.negative_cases["duplicate_ids"]
        apply_case(self.valid_bundle, case)
        self.assertIn(case["expected_code"], self.issue_codes(self.valid_bundle))

    def test_missing_evidence_anchor_fails(self) -> None:
        case = self.negative_cases["missing_evidence"]
        apply_case(self.valid_bundle, case)
        issues = validate_review.validate_bundle(self.valid_bundle)
        self.assertTrue(
            any(
                issue.code == case["expected_code"]
                and issue.path == "$.findings[0].anchor"
                for issue in issues
            ),
            issues,
        )

    def test_unresolved_critical_finding_cannot_end_in_accept(self) -> None:
        case = self.negative_cases["unresolved_critical_accept"]
        apply_case(self.valid_bundle, case)
        self.assertIn(case["expected_code"], self.issue_codes(self.valid_bundle))

    def test_same_family_panel_cannot_claim_cross_model_assurance(self) -> None:
        case = self.negative_cases["same_family_assurance_mismatch"]
        apply_case(self.valid_bundle, case)
        self.assertIn(case["expected_code"], self.issue_codes(self.valid_bundle))

    def test_single_model_review_uses_single_pass_assurance(self) -> None:
        self.valid_bundle["reviewers"] = [self.valid_bundle["reviewers"][0]]
        for finding in self.valid_bundle["findings"]:
            finding["reviewer_id"] = "R-GENERAL"
        self.valid_bundle["chair"]["disagreements"] = []
        self.assertIn("same_family_assurance", self.issue_codes(self.valid_bundle))
        self.valid_bundle["assurance"] = "single_pass_advisory"
        self.assertEqual(validate_review.validate_bundle(self.valid_bundle), [])

    def test_single_pass_assurance_rejects_human_reviewer(self) -> None:
        reviewer = self.valid_bundle["reviewers"][0]
        reviewer["kind"] = "human"
        reviewer["model_family"] = None
        self.valid_bundle["reviewers"] = [reviewer]
        for finding in self.valid_bundle["findings"]:
            finding["reviewer_id"] = "R-GENERAL"
        self.valid_bundle["chair"]["disagreements"] = []
        self.valid_bundle["assurance"] = "single_pass_advisory"
        self.assertIn("single_pass_assurance", self.issue_codes(self.valid_bundle))

    def test_standard_multi_reviewer_synthesis_requires_sealed_reports(self) -> None:
        self.valid_bundle["mode"] = "standard"
        reviewer = self.valid_bundle["reviewers"][0]
        reviewer["sealed"] = False
        reviewer["report_sha256"] = None
        reviewer["sealed_at"] = None
        self.assertIn("unsealed_panel_reviewer", self.issue_codes(self.valid_bundle))

    def test_cross_model_assurance_passes_with_distinct_sealed_families(self) -> None:
        self.valid_bundle["assurance"] = "cross_model_advisory"
        self.valid_bundle["reviewers"][1]["model_family"] = "independent/family-v2"
        self.assertEqual(
            validate_review.validate_bundle(
                self.valid_bundle,
                trusted_model_families={
                    "example/family-v1",
                    "independent/family-v2",
                },
            ),
            [],
        )

    def test_every_open_critical_finding_requires_a_chair_blocker(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        self.valid_bundle["chair"]["blockers"] = []
        self.assertIn("missing_critical_blocker", self.issue_codes(self.valid_bundle))

    def test_resolved_critical_finding_does_not_block_accept(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        self.valid_bundle["findings"][0]["status"] = "resolved"
        self.valid_bundle["reviewers"][1]["role"] = "critical_verifier"
        self.valid_bundle["critical_verifications"] = [
            {
                "finding_id": "F-001",
                "verifier_id": "R-SECURITY",
                "status": "downgraded",
                "checked_anchor": True,
                "checked_arithmetic_or_source": True,
                "counterevidence_considered": "The cited definition resolves the original interpretation.",
                "rationale": "A fresh reviewer found that the issue no longer supports Critical severity.",
            }
        ]
        self.valid_bundle["chair"]["blockers"][0]["status"] = "resolved"
        self.valid_bundle["chair"]["final_recommendation"]["decision"] = "accept"
        self.assertEqual(validate_review.validate_bundle(self.valid_bundle), [])

    def test_critical_finding_requires_fresh_verification(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        self.assertIn("missing_critical_verification", self.issue_codes(self.valid_bundle))

    def test_verified_source_status_requires_source_evidence(self) -> None:
        self.valid_bundle["findings"][1]["source_status"]["sources"] = []
        self.assertIn("verification_evidence", self.issue_codes(self.valid_bundle))

    def test_located_anchor_page_must_be_in_manifest_bounds(self) -> None:
        self.valid_bundle["findings"][0]["anchor"]["page"] = 4
        self.assertIn("page_bounds", self.issue_codes(self.valid_bundle))

    def test_valid_interaction_log_snapshot_passes(self) -> None:
        self.attach_valid_interaction()
        self.assertEqual(
            validate_review.validate_bundle(
                self.valid_bundle,
                trusted_initial_review_sha256=self.detached_initial_digest,
            ),
            [],
        )

    def test_first_turn_awaiting_state_has_no_fabricated_author_record(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["interaction_phase"] = "awaiting_author_response"
        log["evidence_artifacts"] = []
        log["author_responses"] = []
        log["re_evaluations"] = []
        log["post_freeze_findings"] = []
        del log["revised_provisional_meta_review"]
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_awaiting_later_round_preserves_prior_completed_rounds(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["interaction_phase"] = "awaiting_author_response"
        log["question_batches"].append(
            {
                "round": 2,
                "issued_at": "2026-07-22T17:30:00-04:00",
                "rationale": "A remaining novelty ambiguity is still decision-relevant after the first answer.",
                "disclosure_mode": "local_only",
                "questions": [
                    {
                        "id": "Q-PENDING",
                        "finding_id": "F-002",
                        "ambiguity": "The closest-work delta is still unclear.",
                        "decision_relevance": "The answer could change the novelty assessment.",
                        "requested_evidence": "Point to the frozen comparison or state that it is missing.",
                        "new_evidence_policy": "not_requested",
                        "evidence_treatment": "Use only a frozen-manuscript pointer.",
                    }
                ],
            }
        )
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_awaiting_first_turn_cannot_prefill_meta_review(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["interaction_phase"] = "awaiting_author_response"
        log["author_responses"] = []
        log["re_evaluations"] = []
        log["revised_provisional_meta_review"][
            "updated_provisional_recommendation"
        ] = "reject"
        self.assertIn("prefilled_interaction_record", self.issue_codes(self.valid_bundle))

    def test_completed_interaction_requires_actual_response_and_reevaluation(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["author_responses"] = []
        log["re_evaluations"] = []
        codes = self.issue_codes(self.valid_bundle)
        self.assertIn("completed_without_response", codes)
        self.assertIn("completed_without_reevaluation", codes)

    def test_interaction_type_is_exact(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["interaction_type"] = "rebuttal"
        self.assertIn("enum", self.issue_codes(self.valid_bundle))

    def test_formal_venue_rebuttal_requires_rules_snapshot(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"][
            "interaction_type"
        ] = "venue_rebuttal_simulation"
        self.assertIn("required", self.issue_codes(self.valid_bundle))

    def test_formal_venue_rebuttal_with_dated_official_rules_passes(self) -> None:
        self.attach_valid_interaction()
        self.set_valid_venue_rebuttal_rules()
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_formal_venue_rebuttal_rejects_bogus_source_locator(self) -> None:
        self.attach_valid_interaction()
        self.set_valid_venue_rebuttal_rules()
        self.valid_bundle["interaction_log"]["venue_rebuttal_rules"][
            "official_source_locators"
        ] = ["not actually a source locator"]
        self.assertIn("venue_rules_locator_format", self.issue_codes(self.valid_bundle))

    def test_formal_venue_rebuttal_rejects_unrelated_external_check(self) -> None:
        self.attach_valid_interaction()
        self.set_valid_venue_rebuttal_rules()
        rules = self.valid_bundle["interaction_log"]["venue_rebuttal_rules"]
        rules["official_source_locators"] = ["https://example.org/paper"]
        rules["external_check_ids"] = ["X-001"]
        self.assertIn("venue_rules_check_purpose", self.issue_codes(self.valid_bundle))

    def test_formal_venue_rebuttal_check_must_match_official_source(self) -> None:
        self.attach_valid_interaction()
        self.set_valid_venue_rebuttal_rules()
        self.valid_bundle["privacy"]["external_checks"][0][
            "purpose"
        ] = "Verify venue author-response rules and policy."
        self.refresh_detached_initial_digest()
        self.valid_bundle["interaction_log"]["venue_rebuttal_rules"][
            "external_check_ids"
        ] = ["X-001"]
        self.assertIn(
            "venue_rules_check_source_mismatch", self.issue_codes(self.valid_bundle)
        )

    def test_formal_venue_rebuttal_accepts_matching_rules_check(self) -> None:
        self.attach_valid_interaction()
        self.set_valid_venue_rebuttal_rules()
        check = self.valid_bundle["privacy"]["external_checks"][0]
        check["purpose"] = "Verify venue author-response rules and policy."
        self.refresh_detached_initial_digest()
        rules = self.valid_bundle["interaction_log"]["venue_rebuttal_rules"]
        rules["official_source_locators"] = ["https://example.org/paper"]
        rules["external_check_ids"] = ["X-001"]
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_snapshot_cannot_predate_reviewer_seal(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["initial_review_snapshot"][
            "frozen_at"
        ] = "2026-07-22T16:11:00-04:00"
        self.assertIn("freeze_before_reviewer_seal", self.issue_codes(self.valid_bundle))

    def test_author_response_cannot_predate_question(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["author_responses"][0][
            "received_at"
        ] = "2026-07-22T16:34:00-04:00"
        self.assertIn("response_before_question", self.issue_codes(self.valid_bundle))

    def test_question_batch_requires_rationale(self) -> None:
        self.attach_valid_interaction()
        del self.valid_bundle["interaction_log"]["question_batches"][0]["rationale"]
        self.assertIn("required", self.issue_codes(self.valid_bundle))

    def test_valid_post_freeze_finding_is_separate_and_treated(self) -> None:
        self.attach_valid_post_freeze_finding()
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_post_freeze_finding_requires_answered_trigger(self) -> None:
        self.attach_valid_post_freeze_finding()
        self.valid_bundle["interaction_log"]["post_freeze_findings"][0]["origin"][
            "question_id"
        ] = "Q-UNANSWERED"
        self.assertIn(
            "post_freeze_trigger_unanswered", self.issue_codes(self.valid_bundle)
        )

    def test_post_freeze_evidence_must_belong_to_triggering_response(self) -> None:
        self.attach_valid_post_freeze_finding()
        self.valid_bundle["interaction_log"]["author_responses"][0][
            "new_evidence_artifact_ids"
        ] = []
        self.assertIn(
            "post_freeze_evidence_origin_mismatch", self.issue_codes(self.valid_bundle)
        )

    def test_every_post_freeze_finding_requires_meta_treatment(self) -> None:
        self.attach_valid_post_freeze_finding()
        self.valid_bundle["interaction_log"]["revised_provisional_meta_review"][
            "post_freeze_finding_treatments"
        ] = []
        self.assertIn(
            "post_freeze_treatment_coverage", self.issue_codes(self.valid_bundle)
        )

    def test_post_freeze_id_cannot_be_folded_into_initial_classification(self) -> None:
        self.attach_valid_post_freeze_finding()
        self.valid_bundle["interaction_log"]["revised_provisional_meta_review"][
            "remaining_finding_ids"
        ].append("PF-001")
        self.assertIn("post_freeze_finding_fold", self.issue_codes(self.valid_bundle))

    def test_critical_post_freeze_finding_cannot_self_verify(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        self.valid_bundle["interaction_log"]["post_freeze_findings"][0][
            "verifier_id"
        ] = "R-GENERAL"
        self.assertIn(
            "post_freeze_self_verification", self.issue_codes(self.valid_bundle)
        )

    def test_critical_post_freeze_finding_requires_declared_verifier_role(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        self.valid_bundle["reviewers"][1]["role"] = "security_threat_model"
        self.assertIn("post_freeze_verifier_role", self.issue_codes(self.valid_bundle))

    def test_critical_post_freeze_finding_requires_sealed_verifier(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        verifier = self.valid_bundle["reviewers"][1]
        verifier["sealed"] = False
        verifier["report_sha256"] = None
        verifier["sealed_at"] = None
        self.assertIn(
            "unsealed_post_freeze_verifier", self.issue_codes(self.valid_bundle)
        )

    def test_critical_post_freeze_finding_requires_interaction_check(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        post_finding = self.valid_bundle["interaction_log"]["post_freeze_findings"][0]
        post_finding["verification_status"] = "not_required"
        post_finding["verified_severity"] = None
        post_finding["checked_evidence"] = False
        post_finding["verification_performed_at"] = None
        post_finding["verification_report_sha256"] = None
        self.assertIn(
            "missing_post_freeze_verification", self.issue_codes(self.valid_bundle)
        )

    def test_critical_post_freeze_verification_cannot_reuse_initial_seal(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        post_finding = self.valid_bundle["interaction_log"]["post_freeze_findings"][0]
        post_finding["verification_report_sha256"] = self.valid_bundle["reviewers"][1][
            "report_sha256"
        ]
        self.assertIn("reused_initial_verifier_seal", self.issue_codes(self.valid_bundle))

    def test_post_freeze_verification_must_follow_response_and_evidence(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        self.valid_bundle["interaction_log"]["post_freeze_findings"][0][
            "verification_performed_at"
        ] = "2026-07-22T17:15:00-04:00"
        self.assertIn(
            "post_freeze_verification_time_order", self.issue_codes(self.valid_bundle)
        )

    def test_unresolved_critical_post_freeze_finding_cannot_drive_decision(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        log = self.valid_bundle["interaction_log"]
        post_finding = log["post_freeze_findings"][0]
        post_finding["verification_status"] = "unresolved"
        post_finding["verified_severity"] = None
        log["revised_provisional_meta_review"][
            "updated_provisional_recommendation"
        ] = "reject"
        self.assertIn(
            "unresolved_post_freeze_affects_decision", self.issue_codes(self.valid_bundle)
        )

    def test_resolved_critical_post_freeze_status_requires_resolved_verification(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        post_finding = self.valid_bundle["interaction_log"]["post_freeze_findings"][0]
        post_finding["status"] = "resolved"
        self.assertIn("post_freeze_status_conflict", self.issue_codes(self.valid_bundle))

    def test_valid_resolved_critical_post_freeze_finding_can_clear_accept_guard(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        log = self.valid_bundle["interaction_log"]
        post_finding = log["post_freeze_findings"][0]
        post_finding["verification_status"] = "resolved"
        post_finding["verified_severity"] = None
        post_finding["status"] = "resolved"
        treatment = log["revised_provisional_meta_review"][
            "post_freeze_finding_treatments"
        ][0]
        treatment["treatment"] = "documented_no_recommendation_change"
        log["revised_provisional_meta_review"][
            "updated_provisional_recommendation"
        ] = "accept"
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_valid_downgraded_critical_post_freeze_finding_can_clear_accept_guard(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        log = self.valid_bundle["interaction_log"]
        post_finding = log["post_freeze_findings"][0]
        post_finding["verification_status"] = "downgraded"
        post_finding["verified_severity"] = "major"
        log["revised_provisional_meta_review"][
            "updated_provisional_recommendation"
        ] = "accept"
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_open_critical_post_freeze_finding_blocks_acceptance(self) -> None:
        self.attach_valid_post_freeze_finding(severity="critical")
        self.valid_bundle["interaction_log"]["revised_provisional_meta_review"][
            "updated_provisional_recommendation"
        ] = "accept"
        self.assertIn(
            "post_freeze_critical_accept_conflict", self.issue_codes(self.valid_bundle)
        )

    def test_new_root_finding_cannot_replace_post_freeze_ledger(self) -> None:
        self.attach_valid_post_freeze_finding()
        log = self.valid_bundle["interaction_log"]
        injected = copy.deepcopy(self.valid_bundle["findings"][0])
        injected["id"] = "F-INJECTED-AFTER-FREEZE"
        self.valid_bundle["findings"].append(injected)
        log["post_freeze_findings"] = []
        log["revised_provisional_meta_review"][
            "post_freeze_finding_treatments"
        ] = []
        log["initial_review_snapshot"]["open_finding_ids"].append(injected["id"])
        log["revised_provisional_meta_review"]["remaining_finding_ids"].append(
            injected["id"]
        )
        log["initial_review_snapshot"][
            "review_sha256"
        ] = validate_review.canonical_initial_review_sha256(
            self.valid_bundle, log["initial_review_snapshot"]["initial_mode"]
        )
        self.assertIn("trusted_snapshot_mismatch", self.issue_codes(self.valid_bundle))

    def test_interaction_requires_exact_answer_category(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["author_responses"][0]["primary_category"] = "clarification"
        self.assertIn("enum", self.issue_codes(self.valid_bundle))

    def test_interaction_cannot_rewrite_frozen_initial_recommendation(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["initial_review_snapshot"]["recommendation"] = "accept"
        self.assertIn("frozen_review_mismatch", self.issue_codes(self.valid_bundle))

    def test_interaction_hash_detects_initial_review_tampering(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["findings"][0]["observation"] = "Rewritten after the interaction began."
        self.assertIn("frozen_review_hash_mismatch", self.issue_codes(self.valid_bundle))

    def test_planned_revision_cannot_resolve_frozen_manuscript(self) -> None:
        self.attach_valid_interaction()
        response = self.valid_bundle["interaction_log"]["author_responses"][0]
        response["primary_category"] = "planned_revision"
        response["planned_revision"] = "Move the definition into the abstract."
        self.assertIn("answer_status_conflict", self.issue_codes(self.valid_bundle))

    def test_new_evidence_is_hashed_linked_and_remains_post_freeze(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["evidence_artifacts"] = [
            {
                "id": "E-001",
                "kind": "new_analysis",
                "label": "Author-supplied subgroup analysis",
                "sha256": "1" * 64,
                "supplied_at": "2026-07-22T17:00:00-04:00",
                "external_disclosure_limit": "local_only",
                "confidentiality_restrictions": "Keep within the authorized chat runtime.",
            }
        ]
        response = log["author_responses"][0]
        response["primary_category"] = "new_unpublished_evidence"
        response["existing_location"] = None
        response["new_evidence_summary"] = "A new subgroup analysis addresses the concern."
        response["new_evidence_artifact_ids"] = ["E-001"]
        reevaluation = log["re_evaluations"][0]
        reevaluation["status"] = "new_evidence_requires_inclusion"
        meta = log["revised_provisional_meta_review"]
        meta["resolved_finding_ids"] = []
        meta["remaining_finding_ids"] = ["F-001", "F-002"]
        meta["new_evidence_dependency_ids"] = ["E-001"]
        self.assertEqual(self.issue_codes(self.valid_bundle), [])

    def test_new_evidence_dependency_cannot_be_omitted(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["evidence_artifacts"] = [
            {
                "id": "E-001",
                "kind": "new_result",
                "label": "Author-supplied robustness result",
                "sha256": "2" * 64,
                "supplied_at": "2026-07-22T17:00:00-04:00",
                "external_disclosure_limit": "local_only",
                "confidentiality_restrictions": "Keep within the authorized chat runtime.",
            }
        ]
        response = log["author_responses"][0]
        response["primary_category"] = "new_unpublished_evidence"
        response["existing_location"] = None
        response["new_evidence_summary"] = "A new result addresses the concern."
        response["new_evidence_artifact_ids"] = ["E-001"]
        log["re_evaluations"][0]["status"] = "new_evidence_requires_inclusion"
        meta = log["revised_provisional_meta_review"]
        meta["resolved_finding_ids"] = []
        meta["remaining_finding_ids"] = ["F-001", "F-002"]
        self.assertIn("evidence_dependency_conflict", self.issue_codes(self.valid_bundle))

    def test_interactive_escalation_to_critical_blocks_acceptance(self) -> None:
        self.attach_valid_interaction()
        reevaluation = self.valid_bundle["interaction_log"]["re_evaluations"][0]
        reevaluation["status"] = "clarified_but_missing_from_manuscript"
        reevaluation["updated_severity"] = "critical"
        meta = self.valid_bundle["interaction_log"]["revised_provisional_meta_review"]
        meta["resolved_finding_ids"] = []
        meta["remaining_finding_ids"] = ["F-001", "F-002"]
        meta["updated_provisional_recommendation"] = "accept"
        self.assertIn("critical_accept_conflict", self.issue_codes(self.valid_bundle))

    def test_multiple_reevaluations_are_order_independent(self) -> None:
        self.attach_valid_interaction()
        log = self.valid_bundle["interaction_log"]
        log["question_batches"][0]["questions"].append(
            {
                "id": "Q-002",
                "finding_id": "F-001",
                "ambiguity": "The author disputes whether the definition is prominent enough.",
                "decision_relevance": "The dispute changes whether the finding is resolved or remains contested.",
                "requested_evidence": "State the strongest reason the current placement is sufficient.",
                "new_evidence_policy": "not_requested",
                "evidence_treatment": "Treat the answer as argument, not as new manuscript evidence.",
            }
        )
        log["author_responses"].append(
            {
                "question_id": "Q-002",
                "received_at": "2026-07-22T17:16:00-04:00",
                "primary_category": "disagreement",
                "response_text": "The current placement is sufficient for the intended audience.",
                "secondary_notes": [],
                "existing_location": None,
                "new_evidence_summary": None,
                "new_evidence_artifact_ids": [],
                "claim_scope_change": None,
                "planned_revision": None,
                "external_disclosure_limit": "local_only",
                "confidentiality_restrictions": "Keep the response local.",
            }
        )
        log["re_evaluations"].append(
            {
                "question_id": "Q-002",
                "finding_id": "F-001",
                "evaluator_reviewer_id": "R-GENERAL",
                "status": "disputed",
                "verification_performed": "Compared the author's interpretation with the frozen passage.",
                "original_severity": "major",
                "updated_severity": "minor",
                "original_confidence": 0.91,
                "updated_confidence": 0.8,
                "rationale": "The evidence exists, but prominence remains a judgment dispute.",
                "required_manuscript_action": "No mandatory action while the disagreement remains recorded.",
            }
        )
        meta = log["revised_provisional_meta_review"]
        meta["resolved_finding_ids"] = []
        meta["remaining_finding_ids"] = ["F-002"]
        meta["disputed_finding_ids"] = ["F-001"]
        forward_codes = self.issue_codes(self.valid_bundle)
        log["re_evaluations"].reverse()
        reverse_codes = self.issue_codes(self.valid_bundle)
        self.assertEqual(forward_codes, [])
        self.assertEqual(reverse_codes, forward_codes)

    def test_interactive_mode_requires_interaction_log(self) -> None:
        self.valid_bundle["mode"] = "interactive"
        self.assertIn("required", self.issue_codes(self.valid_bundle))

    def test_same_family_normalization_rejects_whitespace_bypass(self) -> None:
        self.valid_bundle["assurance"] = "cross_model_advisory"
        self.valid_bundle["reviewers"][1]["model_family"] = " example/family-v1 "
        codes = self.issue_codes(self.valid_bundle)
        self.assertIn("noncanonical_model_family", codes)
        self.assertIn("cross_model_assurance", codes)

    def test_cross_model_assurance_requires_detached_registry(self) -> None:
        self.valid_bundle["assurance"] = "cross_model_advisory"
        self.valid_bundle["reviewers"][1]["model_family"] = "independent/family-v2"
        self.assertIn(
            "untrusted_model_family_registry", self.issue_codes(self.valid_bundle)
        )

    def test_model_family_alias_is_not_a_canonical_identifier(self) -> None:
        self.valid_bundle["assurance"] = "cross_model_advisory"
        self.valid_bundle["reviewers"][1]["model_family"] = "example_family-v1"
        codes = self.issue_codes(self.valid_bundle)
        self.assertIn("noncanonical_model_family", codes)
        self.assertIn("cross_model_assurance", codes)

    def test_detached_registry_rejects_alias_style_identifiers(self) -> None:
        registry = {
            "registry_version": "1.0.0",
            "canonical_families": ["example_family-v1"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_review.load_model_family_registry(path)

    def test_interactive_validation_requires_detached_digest(self) -> None:
        self.attach_valid_interaction()
        self.assertIn(
            "untrusted_snapshot_digest",
            [
                issue.code
                for issue in validate_review.validate_bundle(self.valid_bundle)
            ],
        )

    def test_recomputed_embedded_hash_cannot_replace_detached_digest(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["findings"][0]["observation"] = "Rewritten after rebuttal."
        embedded = self.valid_bundle["interaction_log"]["initial_review_snapshot"]
        embedded["review_sha256"] = validate_review.canonical_initial_review_sha256(
            self.valid_bundle, embedded["initial_mode"]
        )
        self.assertIn("trusted_snapshot_mismatch", self.issue_codes(self.valid_bundle))

    def test_rewritten_initial_report_cannot_replace_detached_digest(self) -> None:
        self.attach_valid_interaction()
        replacement_hash = "9" * 64
        self.valid_bundle["initial_report"] = {
            "label": "replacement-report.md",
            "sha256": replacement_hash,
        }
        snapshot = self.valid_bundle["interaction_log"]["initial_review_snapshot"]
        snapshot["initial_report_label"] = "replacement-report.md"
        snapshot["initial_report_sha256"] = replacement_hash
        snapshot["review_sha256"] = validate_review.canonical_initial_review_sha256(
            self.valid_bundle, snapshot["initial_mode"]
        )
        self.assertIn("trusted_snapshot_mismatch", self.issue_codes(self.valid_bundle))

    def test_post_freeze_evidence_cannot_predate_snapshot(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["evidence_artifacts"] = [
            {
                "id": "E-EARLY",
                "kind": "author_response_attachment",
                "label": "Attachment dated before the review freeze",
                "sha256": "8" * 64,
                "supplied_at": "2026-07-22T16:00:00-04:00",
                "external_disclosure_limit": "local_only",
                "confidentiality_restrictions": "Keep within the authorized chat runtime.",
            }
        ]
        self.assertIn(
            "pre_freeze_interaction_evidence", self.issue_codes(self.valid_bundle)
        )

    def test_response_privacy_limit_constrains_later_question_rounds(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["interaction_log"]["question_batches"].append(
            {
                "round": 2,
                "issued_at": "2026-07-22T17:30:00-04:00",
                "rationale": "A second decision-relevant ambiguity remains after processing the first response.",
                "disclosure_mode": "metadata_only_external_verification",
                "questions": [
                    {
                        "id": "Q-002",
                        "finding_id": "F-002",
                        "ambiguity": "The closest-work relationship remains uncertain.",
                        "decision_relevance": "The answer could change the novelty finding.",
                        "requested_evidence": "Provide an existing manuscript pointer only.",
                        "new_evidence_policy": "not_requested",
                        "evidence_treatment": "Do not treat the response as external-search permission.",
                    }
                ],
            }
        )
        self.assertIn("response_privacy_override", self.issue_codes(self.valid_bundle))

    def test_interaction_cannot_upgrade_partial_input_to_whole_paper_verdict(self) -> None:
        self.attach_valid_interaction()
        self.valid_bundle["input_scope"] = {
            "material_scope": "abstract_only",
            "complete_relevant_artifact_inspected": False,
            "inspected_components": ["Title", "Abstract"],
            "limitations": ["The full paper was not supplied."],
        }
        for finding in self.valid_bundle["findings"]:
            finding["conditional"] = True
        self.valid_bundle["chair"]["final_recommendation"][
            "decision"
        ] = "no_recommendation"
        log = self.valid_bundle["interaction_log"]
        snapshot = log["initial_review_snapshot"]
        snapshot["recommendation"] = "no_recommendation"
        meta = log["revised_provisional_meta_review"]
        meta["initial_recommendation"] = "no_recommendation"
        meta["updated_provisional_recommendation"] = "accept"
        snapshot["review_sha256"] = validate_review.canonical_initial_review_sha256(
            self.valid_bundle, snapshot["initial_mode"]
        )
        issues = validate_review.validate_bundle(
            self.valid_bundle,
            trusted_initial_review_sha256=snapshot["review_sha256"],
        )
        self.assertIn("partial_input_decision", [issue.code for issue in issues])

    def test_full_forensic_requires_sealed_reviewers(self) -> None:
        self.valid_bundle["mode"] = "full-forensic"
        self.valid_bundle["reviewers"][0]["sealed"] = False
        self.valid_bundle["reviewers"][0]["report_sha256"] = None
        self.valid_bundle["reviewers"][0]["sealed_at"] = None
        self.assertIn("unsealed_mode_reviewer", self.issue_codes(self.valid_bundle))

    def test_focused_mode_requires_specialist_and_no_whole_paper_decision(self) -> None:
        self.valid_bundle["mode"] = "focused"
        self.valid_bundle["focus_areas"] = ["ai_data_methods"]
        self.valid_bundle["chair"]["final_recommendation"]["decision"] = "accept"
        codes = self.issue_codes(self.valid_bundle)
        self.assertIn("focused_requires_specialist", codes)
        self.assertIn("focused_scope_decision", codes)

    def test_valid_focused_writing_review_uses_no_recommendation(self) -> None:
        self.valid_bundle["mode"] = "focused"
        self.valid_bundle["focus_areas"] = ["writing_terminology"]
        for finding in self.valid_bundle["findings"]:
            finding["category"] = "writing_terminology"
        self.valid_bundle["chair"]["final_recommendation"][
            "decision"
        ] = "no_recommendation"
        self.assertEqual(validate_review.validate_bundle(self.valid_bundle), [])

    def test_partial_material_requires_conditional_findings(self) -> None:
        self.valid_bundle["input_scope"] = {
            "material_scope": "abstract_only",
            "complete_relevant_artifact_inspected": False,
            "inspected_components": ["Title", "Abstract"],
            "limitations": ["The full paper was not supplied."],
        }
        self.assertIn("partial_input_overclaim", self.issue_codes(self.valid_bundle))

    def test_incomplete_full_manuscript_requires_conditional_findings(self) -> None:
        self.valid_bundle["input_scope"][
            "complete_relevant_artifact_inspected"
        ] = False
        self.assertIn("partial_input_overclaim", self.issue_codes(self.valid_bundle))

    def test_partial_input_cannot_issue_whole_paper_verdict(self) -> None:
        self.valid_bundle["input_scope"] = {
            "material_scope": "abstract_only",
            "complete_relevant_artifact_inspected": False,
            "inspected_components": ["Title", "Abstract"],
            "limitations": ["The full paper was not supplied."],
        }
        for finding in self.valid_bundle["findings"]:
            finding["conditional"] = True
        self.valid_bundle["chair"]["final_recommendation"]["decision"] = "reject"
        self.assertIn("partial_input_decision", self.issue_codes(self.valid_bundle))

    def test_local_only_privacy_rejects_external_check_records(self) -> None:
        self.valid_bundle["privacy"]["mode"] = "local_only"
        self.assertIn("privacy_mode_conflict", self.issue_codes(self.valid_bundle))

    def test_external_verification_requires_logged_external_check(self) -> None:
        self.valid_bundle["privacy"] = {"mode": "local_only", "external_checks": []}
        self.assertIn(
            "external_verification_without_check", self.issue_codes(self.valid_bundle)
        )

    def test_external_finding_must_link_the_exact_logged_source(self) -> None:
        check = self.valid_bundle["privacy"]["external_checks"][0]
        check["source_locators"] = ["https://weather.example/forecast"]
        self.assertIn(
            "external_check_source_mismatch", self.issue_codes(self.valid_bundle)
        )

    def test_re_review_requires_detached_prior_digest(self) -> None:
        self.valid_bundle["mode"] = "re-review"
        verifier = self.valid_bundle["reviewers"][1]
        verifier["role"] = "critical_verifier"
        verifier["prior_review_involvement"] = "did_not_participate"
        self.valid_bundle["re_review_context"] = {
            "prior_review_sha256": "f" * 64,
            "prior_finding_ids": ["F-OLD-001"],
            "resolution_matrix": [
                {
                    "prior_finding_id": "F-OLD-001",
                    "status": "unresolved",
                    "current_finding_id": "F-001",
                    "verifier_id": "R-SECURITY",
                    "revised_anchor": "Revised manuscript page 1, Introduction.",
                    "rationale": "The clearer wording does not yet supply the missing evidence.",
                }
            ],
        }
        self.assertIn(
            "untrusted_prior_review_digest", self.issue_codes(self.valid_bundle)
        )

    def test_re_review_requires_fresh_sealed_critical_verifier(self) -> None:
        self.valid_bundle["mode"] = "re-review"
        verifier = self.valid_bundle["reviewers"][1]
        verifier["role"] = "critical_verifier"
        verifier["prior_review_involvement"] = "did_not_participate"
        verifier["sealed"] = False
        verifier["report_sha256"] = None
        verifier["sealed_at"] = None
        self.assertIn("missing_fresh_reviewer", self.issue_codes(self.valid_bundle))

    def test_valid_re_review_is_bound_to_prior_digest_and_matrix(self) -> None:
        self.valid_bundle["mode"] = "re-review"
        verifier = self.valid_bundle["reviewers"][1]
        verifier["role"] = "critical_verifier"
        verifier["prior_review_involvement"] = "did_not_participate"
        prior_digest = "f" * 64
        self.valid_bundle["re_review_context"] = {
            "prior_review_sha256": prior_digest,
            "prior_finding_ids": ["F-OLD-001"],
            "resolution_matrix": [
                {
                    "prior_finding_id": "F-OLD-001",
                    "status": "unresolved",
                    "current_finding_id": "F-001",
                    "verifier_id": "R-SECURITY",
                    "revised_anchor": "Revised manuscript page 1, Introduction.",
                    "rationale": "The wording improved but the evidence gap remains.",
                }
            ],
        }
        self.assertEqual(
            validate_review.validate_bundle(
                self.valid_bundle,
                trusted_prior_review_sha256=prior_digest,
                trusted_prior_finding_ids={"F-OLD-001"},
            ),
            [],
        )

    def test_full_forensic_mode_requires_declared_specialist_roles(self) -> None:
        self.valid_bundle["mode"] = "full-forensic"
        self.assertIn("missing_mode_role", self.issue_codes(self.valid_bundle))

    def test_critical_verification_must_check_anchor(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        self.valid_bundle["reviewers"][1]["role"] = "critical_verifier"
        self.valid_bundle["critical_verifications"] = [
            {
                "finding_id": "F-001",
                "verifier_id": "R-SECURITY",
                "status": "confirmed",
                "checked_anchor": False,
                "checked_arithmetic_or_source": True,
                "counterevidence_considered": "The verifier considered the preceding definition.",
                "rationale": "The concern remains material.",
            }
        ]
        self.assertIn("verification_incomplete", self.issue_codes(self.valid_bundle))

    def test_critical_verification_requires_declared_verifier_role(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        self.valid_bundle["critical_verifications"] = [
            {
                "finding_id": "F-001",
                "verifier_id": "R-SECURITY",
                "status": "confirmed",
                "checked_anchor": True,
                "checked_arithmetic_or_source": True,
                "counterevidence_considered": "The verifier checked the preceding definition.",
                "rationale": "The concern remains material.",
            }
        ]
        self.assertIn("verifier_role_conflict", self.issue_codes(self.valid_bundle))

    def test_critical_verification_requires_sealed_verifier(self) -> None:
        self.valid_bundle["findings"][0]["severity"] = "critical"
        verifier = self.valid_bundle["reviewers"][1]
        verifier["role"] = "critical_verifier"
        verifier["sealed"] = False
        verifier["report_sha256"] = None
        verifier["sealed_at"] = None
        self.valid_bundle["critical_verifications"] = [
            {
                "finding_id": "F-001",
                "verifier_id": "R-SECURITY",
                "status": "confirmed",
                "checked_anchor": True,
                "checked_arithmetic_or_source": True,
                "counterevidence_considered": "The verifier checked the preceding definition.",
                "rationale": "The concern remains material.",
            }
        ]
        self.assertIn("unsealed_critical_verifier", self.issue_codes(self.valid_bundle))

    def test_schema_file_is_valid_json_and_disclaims_semantic_truth(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "review-bundle.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("does not establish", schema["description"])

    def test_schema_and_validator_enums_do_not_drift(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "review-bundle.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(schema["properties"]["mode"]["enum"]), validate_review.MODES)
        self.assertEqual(
            set(schema["properties"]["assurance"]["enum"]),
            validate_review.ASSURANCE_LEVELS,
        )
        self.assertEqual(
            set(schema["$defs"]["reviewer"]["properties"]["role"]["enum"]),
            validate_review.ROLES,
        )
        self.assertEqual(
            set(schema["$defs"]["findingCategory"]["enum"]),
            validate_review.CATEGORIES,
        )
        self.assertEqual(
            set(schema["$defs"]["sourceStatus"]["properties"]["status"]["enum"]),
            validate_review.SOURCE_STATES,
        )
        self.assertEqual(
            set(
                schema["$defs"]["sourceStatus"]["properties"][
                    "verification_channel"
                ]["enum"]
            ),
            validate_review.VERIFICATION_CHANNELS,
        )
        self.assertEqual(
            set(schema["$defs"]["authorResponse"]["properties"]["primary_category"]["enum"]),
            validate_review.ANSWER_CATEGORIES,
        )
        self.assertEqual(
            set(schema["$defs"]["reEvaluation"]["properties"]["status"]["enum"]),
            validate_review.REEVALUATION_STATES,
        )
        self.assertEqual(
            set(schema["$defs"]["inputScope"]["properties"]["material_scope"]["enum"]),
            validate_review.INPUT_SCOPES,
        )
        self.assertEqual(
            set(schema["$defs"]["privacyRecord"]["properties"]["mode"]["enum"]),
            validate_review.PRIVACY_MODES,
        )
        self.assertEqual(
            set(
                schema["$defs"]["authorResponse"]["properties"][
                    "external_disclosure_limit"
                ]["enum"]
            ),
            validate_review.PRIVACY_MODES,
        )
        self.assertEqual(
            set(
                schema["$defs"]["interactionEvidence"]["properties"][
                    "external_disclosure_limit"
                ]["enum"]
            ),
            validate_review.PRIVACY_MODES,
        )
        self.assertEqual(
            set(schema["$defs"]["interactionEvidence"]["properties"]["kind"]["enum"]),
            validate_review.INTERACTION_EVIDENCE_KINDS,
        )
        self.assertEqual(
            set(
                schema["$defs"]["interactionLog"]["properties"][
                    "interaction_type"
                ]["enum"]
            ),
            validate_review.INTERACTION_TYPES,
        )
        self.assertEqual(
            set(
                schema["$defs"]["interactionLog"]["properties"][
                    "interaction_phase"
                ]["enum"]
            ),
            validate_review.INTERACTION_PHASES,
        )
        self.assertEqual(
            set(
                schema["$defs"]["postFreezeFinding"]["properties"][
                    "verification_status"
                ]["enum"]
            ),
            validate_review.POST_FREEZE_VERIFICATION_STATES,
        )
        self.assertEqual(
            set(schema["$defs"]["postFreezeFinding"]["properties"]["status"]["enum"]),
            validate_review.FINDING_STATES,
        )
        self.assertEqual(
            {
                schema["$defs"]["postFreezeFinding"]["properties"]["origin"][
                    "properties"
                ]["label"]["const"]
            },
            validate_review.POST_FREEZE_FINDING_ORIGINS,
        )
        self.assertEqual(
            set(
                schema["$defs"]["postFreezeFindingTreatment"]["properties"][
                    "treatment"
                ]["enum"]
            ),
            validate_review.POST_FREEZE_META_TREATMENTS,
        )
        self.assertEqual(
            set(
                schema["$defs"]["reReviewContext"]["properties"][
                    "resolution_matrix"
                ]["items"]["properties"]["status"]["enum"]
            ),
            validate_review.RE_REVIEW_STATES,
        )

    def test_cli_exit_codes_and_json_output(self) -> None:
        validator = ROOT / "scripts" / "validate_review.py"
        valid = subprocess.run(
            [sys.executable, str(validator), str(FIXTURES / "valid_bundle.json"), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertTrue(json.loads(valid.stdout)["valid"])

        invalid_bundle = copy.deepcopy(self.valid_bundle)
        invalid_bundle["findings"].append(copy.deepcopy(invalid_bundle["findings"][0]))
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "invalid.json"
            invalid_path.write_text(json.dumps(invalid_bundle), encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(validator), str(invalid_path), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(invalid.returncode, 1, invalid.stderr)
        self.assertFalse(json.loads(invalid.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
