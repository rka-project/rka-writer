#!/usr/bin/env python3
"""Validate a structured AI/cybersecurity manuscript-review bundle.

This validator is deliberately deterministic and uses only Python's standard
library.  Passing validation proves that required fields, identifiers,
cross-references, evidence locators, assurance labels, and chair decisions are
structurally consistent.  It does *not* prove that the review is scientifically
correct, complete, independent, fair, or true.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set
from urllib.parse import urlparse


SUPPORTED_VERSION = "1.0.0"
MODES = {"quick", "standard", "full-forensic", "interactive", "re-review", "focused"}
ASSURANCE_LEVELS = {
    "single_pass_advisory",
    "provisional_advisory",
    "cross_model_advisory",
    "human_panel",
}
ROLES = {
    "general_cs_fast_reader",
    "security_threat_model",
    "ai_methods_statistics",
    "systems_artifact_reproducibility",
    "ethics_disclosure",
    "novelty_advocate",
    "closest_work_skeptic",
    "critical_verifier",
    "other",
}
CATEGORIES = {
    "topic_audience_fit",
    "novelty_related_work",
    "claims_motivation",
    "threat_model_security_goals",
    "security_evaluation",
    "ai_data_methods",
    "systems_design",
    "experiments_statistics",
    "results_external_validity",
    "reproducibility_artifact",
    "ethics_disclosure",
    "citations_factuality",
    "organization_cognitive_load",
    "figures_tables",
    "writing_terminology",
    "venue_policy",
    "other",
}
FOCUS_ROLE_OPTIONS = {
    "topic_audience_fit": {"general_cs_fast_reader"},
    "novelty_related_work": {"novelty_advocate", "closest_work_skeptic"},
    "claims_motivation": {"general_cs_fast_reader", "closest_work_skeptic"},
    "threat_model_security_goals": {"security_threat_model"},
    "security_evaluation": {"security_threat_model"},
    "ai_data_methods": {"ai_methods_statistics"},
    "systems_design": {"systems_artifact_reproducibility"},
    "experiments_statistics": {
        "ai_methods_statistics",
        "systems_artifact_reproducibility",
    },
    "results_external_validity": {
        "ai_methods_statistics",
        "systems_artifact_reproducibility",
    },
    "reproducibility_artifact": {"systems_artifact_reproducibility"},
    "ethics_disclosure": {"ethics_disclosure"},
    "citations_factuality": {"closest_work_skeptic", "general_cs_fast_reader"},
    "organization_cognitive_load": {"general_cs_fast_reader"},
    "figures_tables": {"general_cs_fast_reader"},
    "writing_terminology": {"general_cs_fast_reader"},
    "venue_policy": {"general_cs_fast_reader"},
    "other": {"other", "general_cs_fast_reader"},
}
SEVERITIES = {"critical", "major", "minor"}
JUDGMENT_TYPES = {"observation", "inference", "externally_verified", "open_question"}
FINDING_STATES = {"open", "resolved", "withdrawn"}
SOURCE_STATES = {
    "not_required",
    "not_checked",
    "unverified",
    "blocked_by_privacy",
    "metadata_verified",
    "claim_support_verified",
    "verification_failed",
}
VERIFICATION_CHANNELS = {"not_applicable", "supplied_material", "external_check"}
INPUT_SCOPES = {
    "full_manuscript",
    "partial_manuscript",
    "abstract_only",
    "excerpt",
    "outline",
    "unknown",
}
PRIVACY_MODES = {
    "local_only",
    "metadata_only_external_verification",
    "author_authorized_full_external_check",
}
PRIVACY_RANK = {
    "local_only": 0,
    "metadata_only_external_verification": 1,
    "author_authorized_full_external_check": 2,
}
EXTERNAL_CONTENT_CLASSES = {
    "public_metadata",
    "manuscript_excerpt",
    "figure_or_table",
    "unpublished_result",
    "full_artifact",
    "other_confidential_content",
}
INTERACTION_EVIDENCE_KINDS = {
    "author_response_text",
    "author_response_attachment",
    "new_analysis",
    "new_result",
    "revised_manuscript",
    "other",
}
INTERACTION_TYPES = {"internal_clarification", "venue_rebuttal_simulation"}
INTERACTION_PHASES = {"awaiting_author_response", "completed"}
POST_FREEZE_FINDING_ORIGINS = {"new_in_rebuttal"}
POST_FREEZE_META_TREATMENTS = {
    "affects_provisional_recommendation",
    "documented_no_recommendation_change",
    "deferred_to_new_review",
    "withdrawn_after_verification",
}
POST_FREEZE_VERIFICATION_STATES = {
    "not_required",
    "confirmed",
    "downgraded",
    "resolved",
    "withdrawn",
    "unresolved",
}
ANSWER_CATEGORIES = {
    "already_supported_clarification",
    "new_unpublished_evidence",
    "planned_revision",
    "concession_or_scope_narrowing",
    "disagreement",
    "cannot_answer",
}
REEVALUATION_STATES = {
    "resolved_in_manuscript",
    "clarified_but_missing_from_manuscript",
    "new_evidence_requires_inclusion",
    "planned",
    "conceded",
    "disputed",
    "unresolved",
}
RE_REVIEW_STATES = {"resolved", "partly_resolved", "unresolved", "regressed"}
DECISIONS = {
    "accept",
    "weak_accept",
    "borderline",
    "weak_reject",
    "reject",
    "major_revision",
    "not_ready",
    "no_recommendation",
}
ACCEPTING_DECISIONS = {"accept", "weak_accept"}
SEVERITY_RANK = {"minor": 1, "major": 2, "critical": 3}
ANSWER_STATUS_COMPATIBILITY = {
    "already_supported_clarification": {
        "resolved_in_manuscript",
        "clarified_but_missing_from_manuscript",
        "disputed",
        "unresolved",
    },
    "new_unpublished_evidence": {
        "new_evidence_requires_inclusion",
        "disputed",
        "unresolved",
    },
    "planned_revision": {"planned", "unresolved"},
    "concession_or_scope_narrowing": {"conceded", "unresolved"},
    "disagreement": {"disputed", "unresolved"},
    "cannot_answer": {"unresolved"},
}
MODE_REQUIRED_ROLES = {
    "quick": {"general_cs_fast_reader"},
    "standard": {
        "general_cs_fast_reader",
        "security_threat_model",
        "ai_methods_statistics",
        "systems_artifact_reproducibility",
        "closest_work_skeptic",
    },
    "full-forensic": {
        "general_cs_fast_reader",
        "security_threat_model",
        "ai_methods_statistics",
        "systems_artifact_reproducibility",
        "ethics_disclosure",
        "novelty_advocate",
        "closest_work_skeptic",
        "critical_verifier",
    },
    "re-review": {"general_cs_fast_reader", "critical_verifier"},
    "focused": {"general_cs_fast_reader"},
}
ARTIFACT_KINDS = {"manuscript", "supplement", "appendix", "artifact_document"}
ID_PATTERNS = {
    "artifact": re.compile(r"^A-[A-Za-z0-9._-]+$"),
    "reviewer": re.compile(r"^R-[A-Za-z0-9._-]+$"),
    "finding": re.compile(r"^F-[A-Za-z0-9._-]+$"),
    "blocker": re.compile(r"^B-[A-Za-z0-9._-]+$"),
    "disagreement": re.compile(r"^D-[A-Za-z0-9._-]+$"),
    "question": re.compile(r"^Q-[A-Za-z0-9._-]+$"),
    "evidence": re.compile(r"^E-[A-Za-z0-9._-]+$"),
    "external_check": re.compile(r"^X-[A-Za-z0-9._-]+$"),
    "post_freeze_finding": re.compile(r"^PF-[A-Za-z0-9._-]+$"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
CLAIM_ID_RE = re.compile(r"^(?:C-[A-Za-z0-9._-]+|paper_level)$")
MODEL_FAMILY_ID_RE = re.compile(
    r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?/[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$"
)
PRIOR_REVIEW_INVOLVEMENT = {
    "not_applicable",
    "participated",
    "did_not_participate",
}


@dataclass(frozen=True, order=True)
class ValidationIssue:
    """One deterministic validation failure."""

    path: str
    code: str
    message: str


class DuplicateJSONKey(ValueError):
    """Raised when a JSON object repeats a key."""


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKey(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_number(value: str) -> None:
    raise ValueError(f"non-finite JSON number is not allowed: {value}")


def load_bundle(path: Path) -> Any:
    """Load strict JSON, rejecting duplicate keys and NaN/Infinity."""

    with path.open("r", encoding="utf-8") as handle:
        return json.load(
            handle,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_number,
        )


def load_model_family_registry(path: Path) -> Set[str]:
    """Load a detached, curator-controlled canonical model-family registry.

    The registry is intentionally separate from the review bundle. If a bundle
    could declare its own trusted families, renaming one model family would be
    enough to manufacture cross-model assurance.
    """

    raw = load_bundle(path)
    if not isinstance(raw, dict):
        raise ValueError("model-family registry must be a JSON object")
    if set(raw) != {"registry_version", "canonical_families"}:
        raise ValueError(
            "model-family registry must contain exactly registry_version and canonical_families"
        )
    if raw["registry_version"] != "1.0.0":
        raise ValueError("model-family registry_version must equal 1.0.0")
    families = raw["canonical_families"]
    if not isinstance(families, list) or not families:
        raise ValueError("canonical_families must be a non-empty array")
    result: Set[str] = set()
    for index, family in enumerate(families):
        if not isinstance(family, str) or not MODEL_FAMILY_ID_RE.fullmatch(family):
            raise ValueError(
                f"canonical_families[{index}] must use lowercase provider/family syntax"
            )
        if family in result:
            raise ValueError(f"canonical_families repeats {family!r}")
        result.add(family)
    return result


def canonical_initial_review_sha256(
    root: Mapping[str, Any], initial_mode: Optional[str] = None
) -> str:
    """Hash the canonical review bundle before its interaction log is attached.

    This proves consistency within one bundle. It cannot prove historical
    immutability if an attacker can rewrite both the bundle and every external
    copy of its prior hash.
    """

    initial = {key: value for key, value in root.items() if key != "interaction_log"}
    if initial_mode is not None:
        initial["mode"] = initial_mode
    payload = json.dumps(
        initial,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_json_sha256(value: Any) -> str:
    """Hash a strict canonical JSON value for detached retention."""

    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _add(
    issues: List[ValidationIssue], path: str, code: str, message: str
) -> None:
    issues.append(ValidationIssue(path=path, code=code, message=message))


def _object(
    value: Any,
    path: str,
    issues: List[ValidationIssue],
    required: Iterable[str],
    allowed: Iterable[str],
) -> Optional[Mapping[str, Any]]:
    if not isinstance(value, dict):
        _add(issues, path, "type", "must be an object")
        return None
    required_set = set(required)
    allowed_set = set(allowed)
    for key in sorted(required_set - set(value)):
        _add(issues, f"{path}.{key}", "required", "is required")
    for key in sorted(set(value) - allowed_set):
        _add(issues, f"{path}.{key}", "unknown_field", "is not allowed")
    return value


def _array(
    value: Any,
    path: str,
    issues: List[ValidationIssue],
    *,
    minimum: int = 0,
) -> Optional[List[Any]]:
    if not isinstance(value, list):
        _add(issues, path, "type", "must be an array")
        return None
    if len(value) < minimum:
        _add(issues, path, "min_items", f"must contain at least {minimum} item(s)")
    return value


def _nonempty_string(
    value: Any, path: str, issues: List[ValidationIssue]
) -> Optional[str]:
    if not isinstance(value, str):
        _add(issues, path, "type", "must be a string")
        return None
    if not value.strip():
        _add(issues, path, "empty", "must contain non-whitespace text")
        return None
    return value


def _enum(
    value: Any,
    path: str,
    issues: List[ValidationIssue],
    allowed: Set[str],
) -> Optional[str]:
    checked = _nonempty_string(value, path, issues)
    if checked is not None and checked not in allowed:
        _add(
            issues,
            path,
            "enum",
            "must be one of: " + ", ".join(sorted(allowed)),
        )
        return None
    return checked


def _identifier(
    value: Any,
    path: str,
    issues: List[ValidationIssue],
    kind: str,
) -> Optional[str]:
    checked = _nonempty_string(value, path, issues)
    if checked is not None and not ID_PATTERNS[kind].fullmatch(checked):
        _add(issues, path, "id_format", f"is not a valid {kind} identifier")
        return None
    return checked


def _boolean(value: Any, path: str, issues: List[ValidationIssue]) -> Optional[bool]:
    if not isinstance(value, bool):
        _add(issues, path, "type", "must be a boolean")
        return None
    return value


def _integer(
    value: Any,
    path: str,
    issues: List[ValidationIssue],
    *,
    minimum: Optional[int] = None,
) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int):
        _add(issues, path, "type", "must be an integer")
        return None
    if minimum is not None and value < minimum:
        _add(issues, path, "range", f"must be at least {minimum}")
        return None
    return value


def _confidence(
    value: Any, path: str, issues: List[ValidationIssue]
) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _add(issues, path, "type", "must be a number from 0 through 1")
        return None
    result = float(value)
    if not math.isfinite(result) or result < 0 or result > 1:
        _add(issues, path, "range", "must be a finite number from 0 through 1")
        return None
    return result


def _date_time(
    value: Any, path: str, issues: List[ValidationIssue]
) -> Optional[datetime]:
    checked = _nonempty_string(value, path, issues)
    if checked is None:
        return None
    try:
        parsed = datetime.fromisoformat(checked.replace("Z", "+00:00"))
    except ValueError:
        _add(issues, path, "date_time", "must be an ISO 8601 date-time")
        return None
    if parsed.tzinfo is None:
        _add(issues, path, "date_time", "must include a UTC offset or Z suffix")
        return None
    return parsed


def _date(value: Any, path: str, issues: List[ValidationIssue]) -> None:
    checked = _nonempty_string(value, path, issues)
    if checked is None:
        return
    try:
        date.fromisoformat(checked)
    except ValueError:
        _add(issues, path, "date", "must be an ISO 8601 calendar date")


def _unique_identifiers(
    ids: Sequence[Optional[str]], path: str, issues: List[ValidationIssue]
) -> None:
    seen: Set[str] = set()
    for index, identifier in enumerate(ids):
        if identifier is None:
            continue
        if identifier in seen:
            _add(
                issues,
                f"{path}[{index}].id",
                "duplicate_id",
                f"duplicates identifier {identifier!r}",
            )
        seen.add(identifier)


def _validate_string_array(
    value: Any, path: str, issues: List[ValidationIssue]
) -> None:
    items = _array(value, path, issues)
    if items is None:
        return
    for index, item in enumerate(items):
        _nonempty_string(item, f"{path}[{index}]", issues)


def _validate_input_scope(
    value: Any, issues: List[ValidationIssue]
) -> tuple[Optional[str], Optional[bool]]:
    path = "$.input_scope"
    scope = _object(
        value,
        path,
        issues,
        required={
            "material_scope",
            "complete_relevant_artifact_inspected",
            "inspected_components",
            "limitations",
        },
        allowed={
            "material_scope",
            "complete_relevant_artifact_inspected",
            "inspected_components",
            "limitations",
        },
    )
    if scope is None:
        return None, None
    material_scope = _enum(
        scope.get("material_scope"), f"{path}.material_scope", issues, INPUT_SCOPES
    )
    complete = _boolean(
        scope.get("complete_relevant_artifact_inspected"),
        f"{path}.complete_relevant_artifact_inspected",
        issues,
    )
    _validate_string_array(
        scope.get("inspected_components"), f"{path}.inspected_components", issues
    )
    _validate_string_array(scope.get("limitations"), f"{path}.limitations", issues)
    if material_scope != "full_manuscript" and complete is True:
        _add(
            issues,
            f"{path}.complete_relevant_artifact_inspected",
            "input_scope_conflict",
            "cannot be true unless material_scope is full_manuscript",
        )
    return material_scope, complete


def _validate_privacy_record(
    value: Any, issues: List[ValidationIssue]
) -> Optional[str]:
    path = "$.privacy"
    privacy = _object(
        value,
        path,
        issues,
        required={"mode", "external_checks"},
        allowed={"mode", "external_checks"},
    )
    if privacy is None:
        return None
    mode = _enum(privacy.get("mode"), f"{path}.mode", issues, PRIVACY_MODES)
    checks = _array(privacy.get("external_checks"), f"{path}.external_checks", issues)
    if checks is None:
        return mode
    if mode == "local_only" and checks:
        _add(
            issues,
            f"{path}.external_checks",
            "privacy_mode_conflict",
            "must be empty in local_only mode",
        )
    check_ids: List[Optional[str]] = []
    for index, raw in enumerate(checks):
        item_path = f"{path}.external_checks[{index}]"
        fields = {
            "id",
            "provider",
            "content_class",
            "purpose",
            "source_locators",
            "authorized_by_user",
            "authorized_at",
        }
        check = _object(raw, item_path, issues, required=fields, allowed=fields)
        if check is None:
            check_ids.append(None)
            continue
        check_id = _identifier(
            check.get("id"), f"{item_path}.id", issues, "external_check"
        )
        check_ids.append(check_id)
        _nonempty_string(check.get("provider"), f"{item_path}.provider", issues)
        content_class = _enum(
            check.get("content_class"),
            f"{item_path}.content_class",
            issues,
            EXTERNAL_CONTENT_CLASSES,
        )
        _nonempty_string(check.get("purpose"), f"{item_path}.purpose", issues)
        source_locators = _array(
            check.get("source_locators"), f"{item_path}.source_locators", issues
        )
        checked_locators: List[str] = []
        if source_locators is not None:
            for locator_index, raw_locator in enumerate(source_locators):
                locator = _nonempty_string(
                    raw_locator,
                    f"{item_path}.source_locators[{locator_index}]",
                    issues,
                )
                if locator is not None:
                    checked_locators.append(locator)
            if len(checked_locators) != len(set(checked_locators)):
                _add(
                    issues,
                    f"{item_path}.source_locators",
                    "duplicate_value",
                    "must not repeat source locators",
                )
        authorized = _boolean(
            check.get("authorized_by_user"),
            f"{item_path}.authorized_by_user",
            issues,
        )
        authorized_at = check.get("authorized_at")
        if authorized_at is not None:
            _date_time(authorized_at, f"{item_path}.authorized_at", issues)
        if mode == "metadata_only_external_verification" and content_class not in {
            None,
            "public_metadata",
        }:
            _add(
                issues,
                f"{item_path}.content_class",
                "privacy_mode_conflict",
                "metadata-only verification may disclose only public metadata",
            )
        if content_class not in {None, "public_metadata"}:
            if mode != "author_authorized_full_external_check":
                _add(
                    issues,
                    f"{item_path}.content_class",
                    "privacy_mode_conflict",
                    "confidential content requires author_authorized_full_external_check",
                )
            if authorized is not True or authorized_at is None:
                _add(
                    issues,
                    item_path,
                    "missing_external_authorization",
                    "confidential external disclosure requires explicit user authorization and timestamp",
                )
    _unique_identifiers(check_ids, f"{path}.external_checks", issues)
    return mode


def _validate_initial_report(
    value: Any, issues: List[ValidationIssue]
) -> tuple[Optional[str], Optional[str]]:
    path = "$.initial_report"
    report = _object(
        value,
        path,
        issues,
        required={"label", "sha256"},
        allowed={"label", "sha256"},
    )
    if report is None:
        return None, None
    label = _nonempty_string(report.get("label"), f"{path}.label", issues)
    digest = _nonempty_string(report.get("sha256"), f"{path}.sha256", issues)
    if digest is not None and not SHA256_RE.fullmatch(digest):
        _add(
            issues,
            f"{path}.sha256",
            "sha256",
            "must be 64 lowercase hexadecimal characters",
        )
    return label, digest


def _validate_manifest(
    value: Any, issues: List[ValidationIssue]
) -> Dict[str, int]:
    path = "$.artifact_manifest"
    manifest = _object(
        value,
        path,
        issues,
        required={"artifacts", "text_extraction", "render_inspections"},
        allowed={"artifacts", "text_extraction", "render_inspections"},
    )
    if manifest is None:
        return {}

    artifacts = _array(manifest.get("artifacts"), f"{path}.artifacts", issues, minimum=1)
    artifact_ids: List[Optional[str]] = []
    page_counts: Dict[str, int] = {}
    manuscript_count = 0
    if artifacts is not None:
        for index, raw in enumerate(artifacts):
            item_path = f"{path}.artifacts[{index}]"
            artifact = _object(
                raw,
                item_path,
                issues,
                required={"id", "kind", "path", "sha256", "page_count"},
                allowed={"id", "kind", "path", "sha256", "page_count"},
            )
            if artifact is None:
                artifact_ids.append(None)
                continue
            artifact_id = _identifier(artifact.get("id"), f"{item_path}.id", issues, "artifact")
            artifact_ids.append(artifact_id)
            kind = _enum(artifact.get("kind"), f"{item_path}.kind", issues, ARTIFACT_KINDS)
            if kind == "manuscript":
                manuscript_count += 1
            _nonempty_string(artifact.get("path"), f"{item_path}.path", issues)
            digest = _nonempty_string(artifact.get("sha256"), f"{item_path}.sha256", issues)
            if digest is not None and not SHA256_RE.fullmatch(digest):
                _add(issues, f"{item_path}.sha256", "sha256", "must be 64 lowercase hexadecimal characters")
            page_count = _integer(
                artifact.get("page_count"), f"{item_path}.page_count", issues, minimum=1
            )
            if artifact_id is not None and page_count is not None:
                page_counts[artifact_id] = page_count
        _unique_identifiers(artifact_ids, f"{path}.artifacts", issues)
    if manuscript_count != 1:
        _add(
            issues,
            f"{path}.artifacts",
            "primary_manuscript",
            f"must identify exactly one manuscript artifact; found {manuscript_count}",
        )

    extraction_path = f"{path}.text_extraction"
    extraction = _object(
        manifest.get("text_extraction"),
        extraction_path,
        issues,
        required={"status", "tool", "limitations"},
        allowed={"status", "tool", "limitations"},
    )
    if extraction is not None:
        _enum(
            extraction.get("status"),
            f"{extraction_path}.status",
            issues,
            {"complete", "partial", "not_available"},
        )
        _nonempty_string(extraction.get("tool"), f"{extraction_path}.tool", issues)
        _validate_string_array(extraction.get("limitations"), f"{extraction_path}.limitations", issues)

    render_path = f"{path}.render_inspections"
    inspections = _array(manifest.get("render_inspections"), render_path, issues)
    inspected_artifacts: Set[str] = set()
    if inspections is not None:
        for index, raw in enumerate(inspections):
            item_path = f"{render_path}[{index}]"
            inspection = _object(
                raw,
                item_path,
                issues,
                required={"artifact_id", "status", "pages", "limitations"},
                allowed={"artifact_id", "status", "pages", "limitations"},
            )
            if inspection is None:
                continue
            artifact_id = _identifier(
                inspection.get("artifact_id"), f"{item_path}.artifact_id", issues, "artifact"
            )
            if artifact_id is not None:
                if artifact_id not in page_counts:
                    _add(issues, f"{item_path}.artifact_id", "unknown_reference", "does not reference a manifest artifact")
                if artifact_id in inspected_artifacts:
                    _add(issues, f"{item_path}.artifact_id", "duplicate_inspection", "has more than one render-inspection record")
                inspected_artifacts.add(artifact_id)
            status = _enum(
                inspection.get("status"),
                f"{item_path}.status",
                issues,
                {"complete", "sampled", "not_inspected"},
            )
            pages = _array(inspection.get("pages"), f"{item_path}.pages", issues)
            page_values: List[int] = []
            if pages is not None:
                for page_index, raw_page in enumerate(pages):
                    page_value = _integer(
                        raw_page, f"{item_path}.pages[{page_index}]", issues, minimum=1
                    )
                    if page_value is not None:
                        page_values.append(page_value)
                        if artifact_id in page_counts and page_value > page_counts[artifact_id]:
                            _add(
                                issues,
                                f"{item_path}.pages[{page_index}]",
                                "page_bounds",
                                f"exceeds artifact page count {page_counts[artifact_id]}",
                            )
                if len(page_values) != len(set(page_values)):
                    _add(issues, f"{item_path}.pages", "duplicate_value", "must not repeat page numbers")
            if status == "not_inspected" and page_values:
                _add(issues, f"{item_path}.pages", "inspection_conflict", "must be empty when status is not_inspected")
            if status in {"complete", "sampled"} and not page_values:
                _add(issues, f"{item_path}.pages", "inspection_conflict", f"must list inspected pages when status is {status}")
            if status == "complete" and artifact_id in page_counts:
                expected = set(range(1, page_counts[artifact_id] + 1))
                if set(page_values) != expected:
                    _add(issues, f"{item_path}.pages", "inspection_conflict", "must list every artifact page when status is complete")
            _validate_string_array(inspection.get("limitations"), f"{item_path}.limitations", issues)

    return page_counts


def _validate_reviewers(
    value: Any,
    assurance: Optional[str],
    trusted_model_families: Optional[Set[str]],
    issues: List[ValidationIssue],
) -> Set[str]:
    path = "$.reviewers"
    reviewers = _array(value, path, issues, minimum=1)
    reviewer_ids: List[Optional[str]] = []
    model_families: Set[str] = set()
    human_count = 0
    all_model = True
    all_sealed = True
    if reviewers is None:
        return set()

    for index, raw in enumerate(reviewers):
        item_path = f"{path}[{index}]"
        reviewer = _object(
            raw,
            item_path,
            issues,
            required={
                "id",
                "role",
                "kind",
                "sealed",
                "report_sha256",
                "sealed_at",
                "model_family",
                "prior_review_involvement",
                "expertise",
                "limitations",
            },
            allowed={
                "id",
                "role",
                "kind",
                "sealed",
                "report_sha256",
                "sealed_at",
                "model_family",
                "prior_review_involvement",
                "expertise",
                "limitations",
            },
        )
        if reviewer is None:
            reviewer_ids.append(None)
            continue
        reviewer_id = _identifier(reviewer.get("id"), f"{item_path}.id", issues, "reviewer")
        reviewer_ids.append(reviewer_id)
        _enum(reviewer.get("role"), f"{item_path}.role", issues, ROLES)
        kind = _enum(reviewer.get("kind"), f"{item_path}.kind", issues, {"model", "human"})
        sealed = _boolean(reviewer.get("sealed"), f"{item_path}.sealed", issues)
        if sealed is False:
            all_sealed = False
        report_sha256 = reviewer.get("report_sha256")
        sealed_at = reviewer.get("sealed_at")
        if sealed is True:
            checked_report_sha256 = _nonempty_string(
                report_sha256, f"{item_path}.report_sha256", issues
            )
            if (
                checked_report_sha256 is not None
                and not SHA256_RE.fullmatch(checked_report_sha256)
            ):
                _add(
                    issues,
                    f"{item_path}.report_sha256",
                    "sha256",
                    "must be 64 lowercase hexadecimal characters",
                )
            if sealed_at is None:
                _add(
                    issues,
                    f"{item_path}.sealed_at",
                    "required",
                    "is required when sealed is true",
                )
            else:
                _date_time(sealed_at, f"{item_path}.sealed_at", issues)
        else:
            if report_sha256 is not None:
                _add(
                    issues,
                    f"{item_path}.report_sha256",
                    "sealing_conflict",
                    "must be null when sealed is false",
                )
            if sealed_at is not None:
                _add(
                    issues,
                    f"{item_path}.sealed_at",
                    "sealing_conflict",
                    "must be null when sealed is false",
                )
        model_family = reviewer.get("model_family")
        if kind == "model":
            checked_family = _nonempty_string(model_family, f"{item_path}.model_family", issues)
            if checked_family is not None:
                if not MODEL_FAMILY_ID_RE.fullmatch(checked_family):
                    _add(
                        issues,
                        f"{item_path}.model_family",
                        "noncanonical_model_family",
                        "must use an exact lowercase provider/family identifier from the detached registry",
                    )
                else:
                    model_families.add(checked_family)
        elif kind == "human":
            human_count += 1
            all_model = False
            if model_family is not None:
                _add(issues, f"{item_path}.model_family", "kind_conflict", "must be null for a human reviewer")
        _enum(
            reviewer.get("prior_review_involvement"),
            f"{item_path}.prior_review_involvement",
            issues,
            PRIOR_REVIEW_INVOLVEMENT,
        )
        _validate_string_array(reviewer.get("expertise"), f"{item_path}.expertise", issues)
        _validate_string_array(reviewer.get("limitations"), f"{item_path}.limitations", issues)

    _unique_identifiers(reviewer_ids, path, issues)
    reviewer_count = len(reviewers)
    if all_model and reviewer_count >= 1 and len(model_families) <= 1:
        expected_assurance = (
            "single_pass_advisory" if reviewer_count == 1 else "provisional_advisory"
        )
        if assurance not in {None, expected_assurance}:
            _add(
                issues,
                "$.assurance",
                "same_family_assurance",
                f"this all-model same-family review must be labeled {expected_assurance}",
            )
    if assurance == "single_pass_advisory":
        if reviewer_count != 1:
            _add(
                issues,
                "$.assurance",
                "single_pass_assurance",
                "single_pass_advisory requires exactly one declared reviewer",
            )
        elif not all_model:
            _add(
                issues,
                "$.assurance",
                "single_pass_assurance",
                "single_pass_advisory requires its sole reviewer to be a model",
            )
    if assurance == "cross_model_advisory":
        if trusted_model_families is None:
            _add(
                issues,
                "$.assurance",
                "untrusted_model_family_registry",
                "cross_model_advisory requires a detached trusted model-family registry",
            )
            registered_families: Set[str] = set()
        else:
            registered_families = model_families & trusted_model_families
            for family in sorted(model_families - trusted_model_families):
                _add(
                    issues,
                    "$.reviewers",
                    "unregistered_model_family",
                    f"model family {family!r} is not in the detached trusted registry",
                )
        if len(registered_families) < 2:
            _add(
                issues,
                "$.assurance",
                "cross_model_assurance",
                "requires at least two distinct canonical families in the detached trusted registry",
            )
        if not all_sealed:
            _add(issues, "$.assurance", "cross_model_assurance", "requires every reviewer report to be sealed")
    if assurance == "human_panel" and human_count < 2:
        _add(issues, "$.assurance", "human_panel_assurance", "requires at least two human reviewers")
    return {identifier for identifier in reviewer_ids if identifier is not None}


def _validate_mode_roles(
    mode: Optional[str], value: Any, issues: List[ValidationIssue]
) -> None:
    """Enforce the reviewer coverage promised by named review modes."""

    required_roles = MODE_REQUIRED_ROLES.get(mode or "")
    if required_roles is None or not isinstance(value, list):
        return
    declared_roles = {
        reviewer.get("role")
        for reviewer in value
        if isinstance(reviewer, dict) and isinstance(reviewer.get("role"), str)
    }
    for role in sorted(required_roles - declared_roles):
        _add(
            issues,
            "$.reviewers",
            "missing_mode_role",
            f"mode {mode!r} requires reviewer role {role!r}",
        )

    if mode == "full-forensic":
        for index, reviewer in enumerate(value):
            if isinstance(reviewer, dict) and reviewer.get("sealed") is not True:
                _add(
                    issues,
                    f"$.reviewers[{index}].sealed",
                    "unsealed_mode_reviewer",
                    "full-forensic mode requires every reviewer report to be sealed before synthesis",
                )

    if mode in {"standard", "interactive", "re-review"} and len(value) > 1:
        for index, reviewer in enumerate(value):
            if isinstance(reviewer, dict) and reviewer.get("sealed") is not True:
                _add(
                    issues,
                    f"$.reviewers[{index}].sealed",
                    "unsealed_panel_reviewer",
                    f"multi-reviewer {mode} synthesis requires every reviewer report to be sealed",
                )

    involvements = {
        reviewer.get("prior_review_involvement")
        for reviewer in value
        if isinstance(reviewer, dict)
    }
    if mode == "re-review":
        fresh_verifiers = [
            reviewer
            for reviewer in value
            if isinstance(reviewer, dict)
            and reviewer.get("role") == "critical_verifier"
            and reviewer.get("prior_review_involvement") == "did_not_participate"
            and reviewer.get("sealed") is True
        ]
        if not fresh_verifiers:
            _add(
                issues,
                "$.reviewers",
                "missing_fresh_reviewer",
                "re-review mode requires a sealed critical verifier who did not participate in the prior review",
            )
    elif mode not in {None, "interactive"}:
        for index, reviewer in enumerate(value):
            if (
                isinstance(reviewer, dict)
                and reviewer.get("prior_review_involvement") != "not_applicable"
            ):
                _add(
                    issues,
                    f"$.reviewers[{index}].prior_review_involvement",
                    "prior_review_mode_conflict",
                    "must be not_applicable outside re-review mode",
                )


def _validate_focus_scope(
    mode: Optional[str], root: Mapping[str, Any], issues: List[ValidationIssue]
) -> None:
    """Require an explicit scientific scope for focused reviews."""

    if mode == "interactive":
        return
    if mode != "focused":
        if "focus_areas" in root:
            _add(
                issues,
                "$.focus_areas",
                "focus_scope_conflict",
                "is allowed only for focused mode or an interactive review whose initial mode was focused",
            )
        return
    focus_areas = _array(root.get("focus_areas"), "$.focus_areas", issues, minimum=1)
    if focus_areas is None:
        return
    checked: List[str] = []
    for index, value in enumerate(focus_areas):
        area = _enum(value, f"$.focus_areas[{index}]", issues, CATEGORIES)
        if area is not None:
            checked.append(area)
    if len(checked) != len(set(checked)):
        _add(issues, "$.focus_areas", "duplicate_value", "must not repeat focus areas")
    declared_roles = {
        reviewer.get("role")
        for reviewer in root.get("reviewers", [])
        if isinstance(reviewer, dict)
    }
    for area in sorted(set(checked)):
        if not declared_roles & FOCUS_ROLE_OPTIONS[area]:
            _add(
                issues,
                "$.reviewers",
                "focused_requires_specialist",
                f"focus area {area!r} requires one of: "
                + ", ".join(sorted(FOCUS_ROLE_OPTIONS[area])),
            )
    chair = root.get("chair")
    decision = None
    if isinstance(chair, dict) and isinstance(chair.get("final_recommendation"), dict):
        decision = chair["final_recommendation"].get("decision")
    if decision != "no_recommendation":
        _add(
            issues,
            "$.chair.final_recommendation.decision",
            "focused_scope_decision",
            "focused mode must use no_recommendation rather than a whole-paper verdict",
        )


def _validate_focused_findings(
    mode: Optional[str],
    root: Mapping[str, Any],
    findings: Mapping[str, Mapping[str, Any]],
    issues: List[ValidationIssue],
) -> None:
    if mode != "focused":
        return
    focus_areas = set(root.get("focus_areas", []))
    for finding_id, finding in findings.items():
        category = finding.get("category")
        if category not in focus_areas:
            _add(
                issues,
                "$.findings",
                "finding_outside_focus",
                f"finding {finding_id!r} uses category {category!r} outside focus_areas",
            )


def _validate_re_review_context(
    mode: Optional[str],
    root: Mapping[str, Any],
    findings: Mapping[str, Mapping[str, Any]],
    trusted_prior_review_sha256: Optional[str],
    trusted_prior_finding_ids: Optional[Set[str]],
    issues: List[ValidationIssue],
) -> None:
    """Bind a re-review to a retained prior review and complete resolution matrix."""

    if mode == "interactive":
        return
    if mode != "re-review":
        if "re_review_context" in root:
            _add(
                issues,
                "$.re_review_context",
                "re_review_mode_conflict",
                "is allowed only for re-review mode or interaction after a re-review",
            )
        return

    path = "$.re_review_context"
    context = _object(
        root.get("re_review_context"),
        path,
        issues,
        required={"prior_review_sha256", "prior_finding_ids", "resolution_matrix"},
        allowed={"prior_review_sha256", "prior_finding_ids", "resolution_matrix"},
    )
    if context is None:
        return
    digest = _nonempty_string(
        context.get("prior_review_sha256"), f"{path}.prior_review_sha256", issues
    )
    if digest is not None and not SHA256_RE.fullmatch(digest):
        _add(
            issues,
            f"{path}.prior_review_sha256",
            "sha256",
            "must be 64 lowercase hexadecimal characters",
        )
    if trusted_prior_review_sha256 is None:
        _add(
            issues,
            f"{path}.prior_review_sha256",
            "untrusted_prior_review_digest",
            "re-review validation requires the detached digest retained with the prior review",
        )
    elif not SHA256_RE.fullmatch(trusted_prior_review_sha256):
        _add(
            issues,
            f"{path}.prior_review_sha256",
            "trusted_prior_review_digest_format",
            "the detached prior-review digest must be 64 lowercase hexadecimal characters",
        )
    elif digest is not None and digest != trusted_prior_review_sha256:
        _add(
            issues,
            f"{path}.prior_review_sha256",
            "trusted_prior_review_mismatch",
            "does not match the detached retained prior-review digest",
        )

    raw_prior_ids = _array(
        context.get("prior_finding_ids"), f"{path}.prior_finding_ids", issues, minimum=1
    )
    prior_ids: List[str] = []
    if raw_prior_ids is not None:
        for index, raw_id in enumerate(raw_prior_ids):
            prior_id = _identifier(
                raw_id, f"{path}.prior_finding_ids[{index}]", issues, "finding"
            )
            if prior_id is not None:
                prior_ids.append(prior_id)
        if len(prior_ids) != len(set(prior_ids)):
            _add(
                issues,
                f"{path}.prior_finding_ids",
                "duplicate_value",
                "must not repeat prior finding identifiers",
            )
    if trusted_prior_finding_ids is None:
        _add(
            issues,
            f"{path}.prior_finding_ids",
            "untrusted_prior_finding_manifest",
            "re-review validation requires finding IDs loaded from the retained prior bundle",
        )
    elif set(prior_ids) != trusted_prior_finding_ids:
        _add(
            issues,
            f"{path}.prior_finding_ids",
            "trusted_prior_finding_mismatch",
            "must exactly match the findings in the retained prior bundle",
        )

    matrix = _array(
        context.get("resolution_matrix"),
        f"{path}.resolution_matrix",
        issues,
        minimum=1,
    )
    covered_prior_ids: List[str] = []
    if matrix is not None:
        fields = {
            "prior_finding_id",
            "status",
            "current_finding_id",
            "verifier_id",
            "revised_anchor",
            "rationale",
        }
        reviewers_by_id = {
            reviewer.get("id"): reviewer
            for reviewer in root.get("reviewers", [])
            if isinstance(reviewer, dict) and isinstance(reviewer.get("id"), str)
        }
        for index, raw in enumerate(matrix):
            item_path = f"{path}.resolution_matrix[{index}]"
            entry = _object(raw, item_path, issues, required=fields, allowed=fields)
            if entry is None:
                continue
            prior_id = _identifier(
                entry.get("prior_finding_id"),
                f"{item_path}.prior_finding_id",
                issues,
                "finding",
            )
            if prior_id is not None:
                covered_prior_ids.append(prior_id)
                if prior_id not in prior_ids:
                    _add(
                        issues,
                        f"{item_path}.prior_finding_id",
                        "unknown_reference",
                        "is not listed in prior_finding_ids",
                    )
            status = _enum(
                entry.get("status"), f"{item_path}.status", issues, RE_REVIEW_STATES
            )
            verifier_id = _identifier(
                entry.get("verifier_id"),
                f"{item_path}.verifier_id",
                issues,
                "reviewer",
            )
            verifier = reviewers_by_id.get(verifier_id)
            if verifier is None and verifier_id is not None:
                _add(
                    issues,
                    f"{item_path}.verifier_id",
                    "unknown_reference",
                    "does not reference a declared re-reviewer",
                )
            elif verifier is not None and not (
                verifier.get("role") == "critical_verifier"
                and verifier.get("prior_review_involvement") == "did_not_participate"
                and verifier.get("sealed") is True
            ):
                _add(
                    issues,
                    f"{item_path}.verifier_id",
                    "re_review_verifier_conflict",
                    "each prior finding must be assessed by a sealed fresh critical verifier",
                )
            current_id = entry.get("current_finding_id")
            checked_current_id: Optional[str] = None
            if current_id is not None:
                checked_current_id = _identifier(
                    current_id,
                    f"{item_path}.current_finding_id",
                    issues,
                    "finding",
                )
                if checked_current_id is not None and checked_current_id not in findings:
                    _add(
                        issues,
                        f"{item_path}.current_finding_id",
                        "unknown_reference",
                        "does not reference a finding in the re-review bundle",
                    )
            if status in {"partly_resolved", "unresolved", "regressed"} and checked_current_id is None:
                _add(
                    issues,
                    f"{item_path}.current_finding_id",
                    "required",
                    f"is required when re-review status is {status}",
                )
            _nonempty_string(
                entry.get("revised_anchor"), f"{item_path}.revised_anchor", issues
            )
            _nonempty_string(entry.get("rationale"), f"{item_path}.rationale", issues)
    if set(covered_prior_ids) != set(prior_ids) or len(covered_prior_ids) != len(
        set(covered_prior_ids)
    ):
        _add(
            issues,
            f"{path}.resolution_matrix",
            "resolution_matrix_coverage",
            "must cover every prior finding exactly once",
        )


def _validate_source_status(
    value: Any, path: str, issues: List[ValidationIssue]
) -> None:
    source_status = _object(
        value,
        path,
        issues,
        required={
            "status",
            "verification_channel",
            "external_check_ids",
            "note",
            "sources",
        },
        allowed={
            "status",
            "verification_channel",
            "external_check_ids",
            "note",
            "sources",
        },
    )
    if source_status is None:
        return
    status = _enum(source_status.get("status"), f"{path}.status", issues, SOURCE_STATES)
    channel = _enum(
        source_status.get("verification_channel"),
        f"{path}.verification_channel",
        issues,
        VERIFICATION_CHANNELS,
    )
    if status in {"metadata_verified", "claim_support_verified"} and channel not in {
        "supplied_material",
        "external_check",
    }:
        _add(
            issues,
            f"{path}.verification_channel",
            "verification_channel_conflict",
            "verified status requires supplied_material or external_check",
        )
    if status in {"not_required", "not_checked", "unverified", "blocked_by_privacy"} and channel not in {
        None,
        "not_applicable",
    }:
        _add(
            issues,
            f"{path}.verification_channel",
            "verification_channel_conflict",
            f"status {status!r} requires not_applicable",
        )
    raw_check_ids = _array(
        source_status.get("external_check_ids"), f"{path}.external_check_ids", issues
    )
    checked_check_ids: List[str] = []
    if raw_check_ids is not None:
        for index, raw_check_id in enumerate(raw_check_ids):
            check_id = _identifier(
                raw_check_id,
                f"{path}.external_check_ids[{index}]",
                issues,
                "external_check",
            )
            if check_id is not None:
                checked_check_ids.append(check_id)
        if len(checked_check_ids) != len(set(checked_check_ids)):
            _add(
                issues,
                f"{path}.external_check_ids",
                "duplicate_value",
                "must not repeat external-check identifiers",
            )
        if channel == "external_check" and not checked_check_ids:
            _add(
                issues,
                f"{path}.external_check_ids",
                "external_check_link_missing",
                "external_check channel requires at least one linked check ID",
            )
        if channel != "external_check" and checked_check_ids:
            _add(
                issues,
                f"{path}.external_check_ids",
                "verification_channel_conflict",
                "must be empty unless verification_channel is external_check",
            )
    _nonempty_string(source_status.get("note"), f"{path}.note", issues)
    sources = _array(source_status.get("sources"), f"{path}.sources", issues)
    if sources is None:
        return
    if status in {"metadata_verified", "claim_support_verified"} and not sources:
        _add(issues, f"{path}.sources", "verification_evidence", f"must list at least one source when status is {status}")
    for index, raw in enumerate(sources):
        item_path = f"{path}.sources[{index}]"
        source = _object(
            raw,
            item_path,
            issues,
            required={"title", "accessed_at"},
            allowed={"title", "url", "doi", "accessed_at"},
        )
        if source is None:
            continue
        _nonempty_string(source.get("title"), f"{item_path}.title", issues)
        url = source.get("url")
        doi = source.get("doi")
        if url is None and doi is None:
            _add(issues, item_path, "source_locator", "must include url or doi")
        if url is not None:
            checked_url = _nonempty_string(url, f"{item_path}.url", issues)
            if checked_url is not None:
                parsed = urlparse(checked_url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    _add(issues, f"{item_path}.url", "url", "must be an absolute http(s) URL")
        if doi is not None:
            _nonempty_string(doi, f"{item_path}.doi", issues)
        _date(source.get("accessed_at"), f"{item_path}.accessed_at", issues)


def _validate_findings(
    value: Any,
    reviewer_ids: Set[str],
    page_counts: Mapping[str, int],
    material_scope: Optional[str],
    complete_relevant_artifact_inspected: Optional[bool],
    issues: List[ValidationIssue],
) -> Dict[str, Mapping[str, Any]]:
    path = "$.findings"
    findings = _array(value, path, issues)
    finding_ids: List[Optional[str]] = []
    result: Dict[str, Mapping[str, Any]] = {}
    if findings is None:
        return result
    required = {
        "id",
        "reviewer_id",
        "claim_id",
        "category",
        "severity",
        "confidence",
        "conditional",
        "status",
        "anchor",
        "observation",
        "judgment_type",
        "affected_claim",
        "reviewer_consequence",
        "repair",
        "verification_test",
        "source_status",
    }
    for index, raw in enumerate(findings):
        item_path = f"{path}[{index}]"
        finding = _object(raw, item_path, issues, required=required, allowed=required)
        if finding is None:
            finding_ids.append(None)
            continue
        finding_id = _identifier(finding.get("id"), f"{item_path}.id", issues, "finding")
        finding_ids.append(finding_id)
        if finding_id is not None and finding_id not in result:
            result[finding_id] = finding
        reviewer_id = _identifier(
            finding.get("reviewer_id"), f"{item_path}.reviewer_id", issues, "reviewer"
        )
        if reviewer_id is not None and reviewer_id not in reviewer_ids:
            _add(issues, f"{item_path}.reviewer_id", "unknown_reference", "does not reference a declared reviewer")
        claim_id = _nonempty_string(finding.get("claim_id"), f"{item_path}.claim_id", issues)
        if claim_id is not None and not CLAIM_ID_RE.fullmatch(claim_id):
            _add(issues, f"{item_path}.claim_id", "id_format", "must be paper_level or a C- prefixed claim identifier")
        _enum(finding.get("category"), f"{item_path}.category", issues, CATEGORIES)
        _enum(finding.get("severity"), f"{item_path}.severity", issues, SEVERITIES)
        _confidence(finding.get("confidence"), f"{item_path}.confidence", issues)
        conditional = _boolean(
            finding.get("conditional"), f"{item_path}.conditional", issues
        )
        _enum(finding.get("status"), f"{item_path}.status", issues, FINDING_STATES)

        anchor_path = f"{item_path}.anchor"
        anchor_status: Optional[str] = None
        anchor = _object(
            finding.get("anchor"),
            anchor_path,
            issues,
            required={"status"},
            allowed={"status", "artifact_id", "page", "section", "locator", "quote", "search_scope", "reason"},
        )
        if anchor is not None:
            anchor_status = _enum(anchor.get("status"), f"{anchor_path}.status", issues, {"located", "not_located"})
            artifact_id: Optional[str] = None
            if "artifact_id" not in anchor:
                _add(issues, f"{anchor_path}.artifact_id", "required", "is required")
            else:
                artifact_id = _identifier(anchor.get("artifact_id"), f"{anchor_path}.artifact_id", issues, "artifact")
                if artifact_id is not None and artifact_id not in page_counts:
                    _add(issues, f"{anchor_path}.artifact_id", "unknown_reference", "does not reference a manifest artifact")
            if anchor_status == "located":
                for key in ("page", "locator", "quote"):
                    if key not in anchor:
                        _add(issues, f"{anchor_path}.{key}", "required", "is required for a located anchor")
                forbidden = {"search_scope", "reason"} & set(anchor)
                for key in sorted(forbidden):
                    _add(issues, f"{anchor_path}.{key}", "anchor_conflict", "is not allowed for a located anchor")
                page = _integer(anchor.get("page"), f"{anchor_path}.page", issues, minimum=1) if "page" in anchor else None
                if page is not None and artifact_id in page_counts and page > page_counts[artifact_id]:
                    _add(issues, f"{anchor_path}.page", "page_bounds", f"exceeds artifact page count {page_counts[artifact_id]}")
                if "section" in anchor:
                    _nonempty_string(anchor.get("section"), f"{anchor_path}.section", issues)
                if "locator" in anchor:
                    _nonempty_string(anchor.get("locator"), f"{anchor_path}.locator", issues)
                if "quote" in anchor:
                    _nonempty_string(anchor.get("quote"), f"{anchor_path}.quote", issues)
            elif anchor_status == "not_located":
                for key in ("search_scope", "reason"):
                    if key not in anchor:
                        _add(issues, f"{anchor_path}.{key}", "required", "is required for an honest not_located anchor")
                    else:
                        _nonempty_string(anchor.get(key), f"{anchor_path}.{key}", issues)
                forbidden = {"page", "section", "locator", "quote"} & set(anchor)
                for key in sorted(forbidden):
                    _add(issues, f"{anchor_path}.{key}", "anchor_conflict", "is not allowed for a not_located anchor")

        for key in (
            "observation",
            "affected_claim",
            "reviewer_consequence",
            "repair",
            "verification_test",
        ):
            _nonempty_string(finding.get(key), f"{item_path}.{key}", issues)
        judgment_type = _enum(
            finding.get("judgment_type"),
            f"{item_path}.judgment_type",
            issues,
            JUDGMENT_TYPES,
        )
        if (
            material_scope is not None
            and (
                material_scope != "full_manuscript"
                or complete_relevant_artifact_inspected is not True
            )
            and conditional is not True
        ):
            _add(
                issues,
                f"{item_path}.conditional",
                "partial_input_overclaim",
                "findings must be conditional unless the full relevant manuscript was inspected",
            )
        _validate_source_status(finding.get("source_status"), f"{item_path}.source_status", issues)

    _unique_identifiers(finding_ids, path, issues)
    return result


def _validate_finding_verification_privacy(
    privacy_mode: Optional[str],
    privacy_value: Any,
    findings: Mapping[str, Mapping[str, Any]],
    issues: List[ValidationIssue],
) -> None:
    external_checks = []
    checks_by_id: Dict[str, Set[str]] = {}
    if isinstance(privacy_value, dict) and isinstance(
        privacy_value.get("external_checks"), list
    ):
        external_checks = privacy_value["external_checks"]
        for check in external_checks:
            if (
                isinstance(check, dict)
                and isinstance(check.get("id"), str)
                and isinstance(check.get("source_locators"), list)
            ):
                checks_by_id[check["id"]] = {
                    locator
                    for locator in check["source_locators"]
                    if isinstance(locator, str)
                }
    for finding_id, finding in findings.items():
        source_status = finding.get("source_status")
        if not isinstance(source_status, dict):
            continue
        status = source_status.get("status")
        channel = source_status.get("verification_channel")
        if channel == "external_check" and (
            privacy_mode == "local_only" or not external_checks
        ):
            _add(
                issues,
                "$.privacy.external_checks",
                "external_verification_without_check",
                f"finding {finding_id!r} claims an external check that the privacy record does not support",
            )
        if channel == "external_check":
            linked_check_ids = {
                check_id
                for check_id in source_status.get("external_check_ids", [])
                if isinstance(check_id, str)
            }
            for check_id in sorted(linked_check_ids - set(checks_by_id)):
                _add(
                    issues,
                    "$.findings",
                    "unknown_external_check_reference",
                    f"finding {finding_id!r} references undeclared external check {check_id!r}",
                )
            permitted_locators: Set[str] = set()
            for check_id in linked_check_ids:
                permitted_locators.update(checks_by_id.get(check_id, set()))
            source_locators: Set[str] = set()
            for source in source_status.get("sources", []):
                if not isinstance(source, dict):
                    continue
                if isinstance(source.get("url"), str):
                    source_locators.add(source["url"])
                if isinstance(source.get("doi"), str):
                    source_locators.add(source["doi"])
            for locator in sorted(source_locators - permitted_locators):
                _add(
                    issues,
                    "$.findings",
                    "external_check_source_mismatch",
                    f"finding {finding_id!r} source locator {locator!r} is not recorded by its linked external check",
                )
        if (
            finding.get("judgment_type") == "externally_verified"
            and (
                status != "claim_support_verified"
                or channel != "external_check"
            )
        ):
            _add(
                issues,
                "$.findings",
                "externally_verified_support_conflict",
                f"finding {finding_id!r} requires claim_support_verified through external_check",
            )


def _validate_input_scope_decision(
    material_scope: Optional[str],
    complete_relevant_artifact_inspected: Optional[bool],
    root: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if material_scope is None or (
        material_scope == "full_manuscript"
        and complete_relevant_artifact_inspected is True
    ):
        return
    chair = root.get("chair")
    decision = None
    if isinstance(chair, dict) and isinstance(chair.get("final_recommendation"), dict):
        decision = chair["final_recommendation"].get("decision")
    if decision != "no_recommendation":
        _add(
            issues,
            "$.chair.final_recommendation.decision",
            "partial_input_decision",
            "incomplete manuscript inspection requires no_recommendation and a scoped conditional assessment",
        )


def _validate_chair(
    value: Any,
    reviewer_ids: Set[str],
    findings: Mapping[str, Mapping[str, Any]],
    issues: List[ValidationIssue],
) -> None:
    path = "$.chair"
    chair = _object(
        value,
        path,
        issues,
        required={"blockers", "disagreements", "final_recommendation"},
        allowed={"blockers", "disagreements", "final_recommendation"},
    )
    if chair is None:
        return

    blocker_path = f"{path}.blockers"
    blockers = _array(chair.get("blockers"), blocker_path, issues)
    blocker_ids: List[Optional[str]] = []
    unresolved_blocker_findings: Set[str] = set()
    if blockers is not None:
        for index, raw in enumerate(blockers):
            item_path = f"{blocker_path}[{index}]"
            blocker = _object(
                raw,
                item_path,
                issues,
                required={"id", "finding_id", "status", "rationale"},
                allowed={"id", "finding_id", "status", "rationale"},
            )
            if blocker is None:
                blocker_ids.append(None)
                continue
            blocker_ids.append(_identifier(blocker.get("id"), f"{item_path}.id", issues, "blocker"))
            finding_id = _identifier(blocker.get("finding_id"), f"{item_path}.finding_id", issues, "finding")
            if finding_id is not None and finding_id not in findings:
                _add(issues, f"{item_path}.finding_id", "unknown_reference", "does not reference a declared finding")
            status = _enum(blocker.get("status"), f"{item_path}.status", issues, {"resolved", "unresolved"})
            _nonempty_string(blocker.get("rationale"), f"{item_path}.rationale", issues)
            if status == "unresolved" and finding_id is not None:
                unresolved_blocker_findings.add(finding_id)
                finding = findings.get(finding_id)
                if finding is not None and finding.get("status") != "open":
                    _add(issues, f"{item_path}.status", "blocker_state_conflict", "an unresolved blocker must reference an open finding")
        _unique_identifiers(blocker_ids, blocker_path, issues)

    open_critical = {
        finding_id
        for finding_id, finding in findings.items()
        if finding.get("severity") == "critical" and finding.get("status") == "open"
    }
    for finding_id in sorted(open_critical - unresolved_blocker_findings):
        _add(
            issues,
            blocker_path,
            "missing_critical_blocker",
            f"open critical finding {finding_id!r} must have an unresolved chair blocker",
        )

    disagreement_path = f"{path}.disagreements"
    disagreements = _array(chair.get("disagreements"), disagreement_path, issues)
    disagreement_ids: List[Optional[str]] = []
    if disagreements is not None:
        for index, raw in enumerate(disagreements):
            item_path = f"{disagreement_path}[{index}]"
            disagreement = _object(
                raw,
                item_path,
                issues,
                required={"id", "reviewer_ids", "finding_ids", "summary", "resolution_status", "chair_reasoning"},
                allowed={"id", "reviewer_ids", "finding_ids", "summary", "resolution_status", "chair_reasoning"},
            )
            if disagreement is None:
                disagreement_ids.append(None)
                continue
            disagreement_ids.append(_identifier(disagreement.get("id"), f"{item_path}.id", issues, "disagreement"))
            referenced_reviewers = _array(disagreement.get("reviewer_ids"), f"{item_path}.reviewer_ids", issues, minimum=2)
            if referenced_reviewers is not None:
                checked_reviewers: List[str] = []
                for ref_index, raw_id in enumerate(referenced_reviewers):
                    reviewer_id = _identifier(raw_id, f"{item_path}.reviewer_ids[{ref_index}]", issues, "reviewer")
                    if reviewer_id is not None:
                        checked_reviewers.append(reviewer_id)
                        if reviewer_id not in reviewer_ids:
                            _add(issues, f"{item_path}.reviewer_ids[{ref_index}]", "unknown_reference", "does not reference a declared reviewer")
                if len(checked_reviewers) != len(set(checked_reviewers)):
                    _add(issues, f"{item_path}.reviewer_ids", "duplicate_value", "must not repeat reviewer identifiers")
            referenced_findings = _array(disagreement.get("finding_ids"), f"{item_path}.finding_ids", issues, minimum=1)
            if referenced_findings is not None:
                checked_findings: List[str] = []
                for ref_index, raw_id in enumerate(referenced_findings):
                    finding_id = _identifier(raw_id, f"{item_path}.finding_ids[{ref_index}]", issues, "finding")
                    if finding_id is not None:
                        checked_findings.append(finding_id)
                        if finding_id not in findings:
                            _add(issues, f"{item_path}.finding_ids[{ref_index}]", "unknown_reference", "does not reference a declared finding")
                if len(checked_findings) != len(set(checked_findings)):
                    _add(issues, f"{item_path}.finding_ids", "duplicate_value", "must not repeat finding identifiers")
            _nonempty_string(disagreement.get("summary"), f"{item_path}.summary", issues)
            _enum(disagreement.get("resolution_status"), f"{item_path}.resolution_status", issues, {"resolved", "unresolved"})
            _nonempty_string(disagreement.get("chair_reasoning"), f"{item_path}.chair_reasoning", issues)
        _unique_identifiers(disagreement_ids, disagreement_path, issues)

    recommendation_path = f"{path}.final_recommendation"
    recommendation = _object(
        chair.get("final_recommendation"),
        recommendation_path,
        issues,
        required={"decision", "confidence", "rationale"},
        allowed={"decision", "confidence", "rationale"},
    )
    if recommendation is not None:
        decision = _enum(recommendation.get("decision"), f"{recommendation_path}.decision", issues, DECISIONS)
        _confidence(recommendation.get("confidence"), f"{recommendation_path}.confidence", issues)
        _nonempty_string(recommendation.get("rationale"), f"{recommendation_path}.rationale", issues)
        if open_critical and decision in ACCEPTING_DECISIONS:
            listed = ", ".join(sorted(open_critical))
            _add(
                issues,
                f"{recommendation_path}.decision",
                "critical_accept_conflict",
                f"cannot recommend {decision} while critical finding(s) remain open: {listed}",
            )


def _validate_critical_verifications(
    value: Any,
    reviewer_ids: Set[str],
    reviewer_roles: Mapping[str, str],
    reviewer_sealed: Mapping[str, bool],
    findings: Mapping[str, Mapping[str, Any]],
    issues: List[ValidationIssue],
) -> None:
    """Require a fresh, non-originating reviewer check for every Critical finding."""

    path = "$.critical_verifications"
    records = _array(value, path, issues)
    if records is None:
        return
    verified_findings: Set[str] = set()
    required_fields = {
        "finding_id",
        "verifier_id",
        "status",
        "checked_anchor",
        "checked_arithmetic_or_source",
        "counterevidence_considered",
        "rationale",
    }
    for index, raw in enumerate(records):
        item_path = f"{path}[{index}]"
        record = _object(
            raw,
            item_path,
            issues,
            required=required_fields,
            allowed=required_fields,
        )
        if record is None:
            continue
        finding_id = _identifier(
            record.get("finding_id"), f"{item_path}.finding_id", issues, "finding"
        )
        verifier_id = _identifier(
            record.get("verifier_id"), f"{item_path}.verifier_id", issues, "reviewer"
        )
        status = _enum(
            record.get("status"),
            f"{item_path}.status",
            issues,
            {"confirmed", "downgraded", "withdrawn", "unresolved"},
        )
        checked_anchor = _boolean(
            record.get("checked_anchor"), f"{item_path}.checked_anchor", issues
        )
        if checked_anchor is False:
            _add(
                issues,
                f"{item_path}.checked_anchor",
                "verification_incomplete",
                "must be true for a Critical finding verification",
            )
        checked_arithmetic_or_source = _boolean(
            record.get("checked_arithmetic_or_source"),
            f"{item_path}.checked_arithmetic_or_source",
            issues,
        )
        if checked_arithmetic_or_source is False:
            _add(
                issues,
                f"{item_path}.checked_arithmetic_or_source",
                "verification_incomplete",
                "must be true after checking the relevant arithmetic/source or confirming it is not applicable",
            )
        _nonempty_string(
            record.get("counterevidence_considered"),
            f"{item_path}.counterevidence_considered",
            issues,
        )
        _nonempty_string(record.get("rationale"), f"{item_path}.rationale", issues)

        finding = findings.get(finding_id) if finding_id is not None else None
        if finding_id is not None:
            if finding_id in verified_findings:
                _add(
                    issues,
                    f"{item_path}.finding_id",
                    "duplicate_verification",
                    "has more than one primary critical-verification record",
                )
            verified_findings.add(finding_id)
        if finding is None and finding_id is not None:
            _add(
                issues,
                f"{item_path}.finding_id",
                "unknown_reference",
                "does not reference a declared finding",
            )
        elif finding is not None:
            if finding.get("severity") != "critical":
                _add(
                    issues,
                    f"{item_path}.finding_id",
                    "verification_scope",
                    "must reference a Critical finding",
                )
            if verifier_id == finding.get("reviewer_id"):
                _add(
                    issues,
                    f"{item_path}.verifier_id",
                    "self_verification",
                    "must differ from the finding's originating reviewer",
                )
            if finding.get("status") == "open" and status not in {"confirmed", "unresolved"}:
                _add(
                    issues,
                    f"{item_path}.status",
                    "verification_state_conflict",
                    "an open Critical finding must be confirmed or unresolved",
                )
        if verifier_id is not None and verifier_id not in reviewer_ids:
            _add(
                issues,
                f"{item_path}.verifier_id",
                "unknown_reference",
                "does not reference a declared reviewer",
            )
        elif verifier_id is not None and reviewer_roles.get(verifier_id) != "critical_verifier":
            _add(
                issues,
                f"{item_path}.verifier_id",
                "verifier_role_conflict",
                "Critical findings must be checked by the declared critical_verifier role",
            )
        elif verifier_id is not None and reviewer_sealed.get(verifier_id) is not True:
            _add(
                issues,
                f"{item_path}.verifier_id",
                "unsealed_critical_verifier",
                "Critical findings must be checked in a sealed verifier report",
            )

    critical_ids = {
        finding_id
        for finding_id, finding in findings.items()
        if finding.get("severity") == "critical"
    }
    for finding_id in sorted(critical_ids - verified_findings):
        _add(
            issues,
            path,
            "missing_critical_verification",
            f"Critical finding {finding_id!r} requires a fresh verification record",
        )


def _validate_interaction_log(
    value: Any,
    root: Mapping[str, Any],
    findings: Mapping[str, Mapping[str, Any]],
    privacy_mode: Optional[str],
    trusted_initial_review_sha256: Optional[str],
    trusted_prior_review_sha256: Optional[str],
    trusted_prior_finding_ids: Optional[Set[str]],
    issues: List[ValidationIssue],
) -> None:
    """Validate a snapshot-linked clarification/rebuttal record."""

    path = "$.interaction_log"
    required = {
        "interaction_type",
        "interaction_phase",
        "initial_review_snapshot",
        "evidence_artifacts",
        "question_batches",
        "author_responses",
        "re_evaluations",
        "post_freeze_findings",
    }
    allowed = required | {"venue_rebuttal_rules", "revised_provisional_meta_review"}
    log = _object(value, path, issues, required=required, allowed=allowed)
    if log is None:
        return

    interaction_type = _enum(
        log.get("interaction_type"),
        f"{path}.interaction_type",
        issues,
        INTERACTION_TYPES,
    )
    interaction_phase = _enum(
        log.get("interaction_phase"),
        f"{path}.interaction_phase",
        issues,
        INTERACTION_PHASES,
    )

    reviewer_records = {
        reviewer.get("id"): reviewer
        for reviewer in root.get("reviewers", [])
        if isinstance(reviewer, dict) and isinstance(reviewer.get("id"), str)
    }

    rules_path = f"{path}.venue_rebuttal_rules"
    rules_verified_at: Optional[datetime] = None
    if interaction_type == "venue_rebuttal_simulation":
        rules_fields = {
            "venue",
            "year",
            "track",
            "paper_type",
            "stage",
            "verified_at",
            "official_source_locators",
            "external_check_ids",
            "length_rule",
            "scope_rule",
            "link_rule",
            "anonymity_rule",
            "new_evidence_rule",
            "round_rule",
        }
        if "venue_rebuttal_rules" not in log:
            _add(
                issues,
                rules_path,
                "required",
                "is required for venue_rebuttal_simulation",
            )
            rules = None
        else:
            rules = _object(
                log.get("venue_rebuttal_rules"),
                rules_path,
                issues,
                required=rules_fields,
                allowed=rules_fields,
            )
        if rules is not None:
            for key in (
                "venue",
                "track",
                "paper_type",
                "stage",
                "length_rule",
                "scope_rule",
                "link_rule",
                "anonymity_rule",
                "new_evidence_rule",
                "round_rule",
            ):
                _nonempty_string(rules.get(key), f"{rules_path}.{key}", issues)
            _integer(rules.get("year"), f"{rules_path}.year", issues, minimum=2000)
            rules_verified_at = _date_time(
                rules.get("verified_at"), f"{rules_path}.verified_at", issues
            )
            source_locators = _array(
                rules.get("official_source_locators"),
                f"{rules_path}.official_source_locators",
                issues,
            )
            checked_locators: List[str] = []
            if source_locators is not None:
                for index, locator in enumerate(source_locators):
                    checked = _nonempty_string(
                        locator,
                        f"{rules_path}.official_source_locators[{index}]",
                        issues,
                    )
                    if checked is not None:
                        checked_locators.append(checked)
                        parsed_locator = urlparse(checked)
                        valid_http = (
                            parsed_locator.scheme in {"http", "https"}
                            and bool(parsed_locator.netloc)
                        )
                        if not valid_http and DOI_RE.fullmatch(checked) is None:
                            _add(
                                issues,
                                f"{rules_path}.official_source_locators[{index}]",
                                "venue_rules_locator_format",
                                "must be an absolute http(s) URL or DOI",
                            )
                if len(checked_locators) != len(set(checked_locators)):
                    _add(
                        issues,
                        f"{rules_path}.official_source_locators",
                        "duplicate_value",
                        "must not repeat official source locators",
                    )
            external_check_records = {
                check.get("id"): check
                for check in (
                    root.get("privacy", {}).get("external_checks", [])
                    if isinstance(root.get("privacy"), dict)
                    else []
                )
                if isinstance(check, dict) and isinstance(check.get("id"), str)
            }
            rule_check_ids = _array(
                rules.get("external_check_ids"),
                f"{rules_path}.external_check_ids",
                issues,
            )
            checked_rule_ids: List[str] = []
            if rule_check_ids is not None:
                for index, raw_id in enumerate(rule_check_ids):
                    check_id = _identifier(
                        raw_id,
                        f"{rules_path}.external_check_ids[{index}]",
                        issues,
                        "external_check",
                    )
                    if check_id is not None:
                        checked_rule_ids.append(check_id)
                        check = external_check_records.get(check_id)
                        if check is None:
                            _add(
                                issues,
                                f"{rules_path}.external_check_ids[{index}]",
                                "unknown_reference",
                                "does not reference a declared external check",
                            )
                        else:
                            purpose = str(check.get("purpose", "")).lower()
                            purpose_has_context = any(
                                marker in purpose
                                for marker in (
                                    "venue",
                                    "rebuttal",
                                    "author response",
                                    "author-response",
                                )
                            )
                            purpose_has_rule = any(
                                marker in purpose
                                for marker in ("rule", "policy", "instruction")
                            )
                            if not (purpose_has_context and purpose_has_rule):
                                _add(
                                    issues,
                                    f"{rules_path}.external_check_ids[{index}]",
                                    "venue_rules_check_purpose",
                                    "linked external check purpose must explicitly cover venue/rebuttal rules or policy",
                                )
                            check_locators = {
                                locator
                                for locator in check.get("source_locators", [])
                                if isinstance(locator, str)
                            }
                            if not check_locators.intersection(checked_locators):
                                _add(
                                    issues,
                                    f"{rules_path}.external_check_ids[{index}]",
                                    "venue_rules_check_source_mismatch",
                                    "linked external check must share an exact source locator with the official-rules snapshot",
                                )
                if len(checked_rule_ids) != len(set(checked_rule_ids)):
                    _add(
                        issues,
                        f"{rules_path}.external_check_ids",
                        "duplicate_value",
                        "must not repeat external-check identifiers",
                    )
            if not checked_locators:
                _add(
                    issues,
                    rules_path,
                    "venue_rules_source_missing",
                    "formal rebuttal rules require at least one official http(s) URL or DOI locator",
                )
    elif "venue_rebuttal_rules" in log:
        _add(
            issues,
            rules_path,
            "venue_rules_type_conflict",
            "is allowed only for venue_rebuttal_simulation",
        )

    evidence_ids: Set[str] = set()
    evidence_kinds: Dict[str, str] = {}
    evidence_disclosure_limits: Dict[str, str] = {}
    evidence_supplied_times: List[tuple[str, datetime]] = []
    evidence_supplied_at: Dict[str, datetime] = {}
    evidence_path = f"{path}.evidence_artifacts"
    evidence_artifacts = _array(log.get("evidence_artifacts"), evidence_path, issues)
    if evidence_artifacts is not None:
        evidence_fields = {
            "id",
            "kind",
            "label",
            "sha256",
            "supplied_at",
            "external_disclosure_limit",
            "confidentiality_restrictions",
        }
        for index, raw in enumerate(evidence_artifacts):
            item_path = f"{evidence_path}[{index}]"
            evidence = _object(
                raw,
                item_path,
                issues,
                required=evidence_fields,
                allowed=evidence_fields,
            )
            if evidence is None:
                continue
            evidence_id = _identifier(
                evidence.get("id"), f"{item_path}.id", issues, "evidence"
            )
            if evidence_id is not None:
                if evidence_id in evidence_ids:
                    _add(
                        issues,
                        f"{item_path}.id",
                        "duplicate_id",
                        "duplicates an interaction-evidence identifier",
                    )
                evidence_ids.add(evidence_id)
            kind = _enum(
                evidence.get("kind"),
                f"{item_path}.kind",
                issues,
                INTERACTION_EVIDENCE_KINDS,
            )
            if evidence_id is not None and kind is not None:
                evidence_kinds[evidence_id] = kind
            evidence_disclosure_limit = _enum(
                evidence.get("external_disclosure_limit"),
                f"{item_path}.external_disclosure_limit",
                issues,
                PRIVACY_MODES,
            )
            if evidence_id is not None and evidence_disclosure_limit is not None:
                evidence_disclosure_limits[evidence_id] = evidence_disclosure_limit
            _nonempty_string(evidence.get("label"), f"{item_path}.label", issues)
            digest = _nonempty_string(
                evidence.get("sha256"), f"{item_path}.sha256", issues
            )
            if digest is not None and not SHA256_RE.fullmatch(digest):
                _add(
                    issues,
                    f"{item_path}.sha256",
                    "sha256",
                    "must be 64 lowercase hexadecimal characters",
                )
            supplied_at = _date_time(
                evidence.get("supplied_at"), f"{item_path}.supplied_at", issues
            )
            if supplied_at is not None:
                evidence_supplied_times.append((f"{item_path}.supplied_at", supplied_at))
                if evidence_id is not None:
                    evidence_supplied_at[evidence_id] = supplied_at
            _nonempty_string(
                evidence.get("confidentiality_restrictions"),
                f"{item_path}.confidentiality_restrictions",
                issues,
            )

    manifest_hashes: Dict[str, str] = {}
    manifest = root.get("artifact_manifest")
    if isinstance(manifest, dict) and isinstance(manifest.get("artifacts"), list):
        for artifact in manifest["artifacts"]:
            if isinstance(artifact, dict) and isinstance(artifact.get("id"), str) and isinstance(artifact.get("sha256"), str):
                manifest_hashes[artifact["id"]] = artifact["sha256"]
    initial_recommendation = None
    initial_confidence = None
    chair = root.get("chair")
    if isinstance(chair, dict) and isinstance(chair.get("final_recommendation"), dict):
        initial_recommendation = chair["final_recommendation"].get("decision")
        initial_confidence = chair["final_recommendation"].get("confidence")
    current_open = {fid for fid, finding in findings.items() if finding.get("status") == "open"}

    frozen_at: Optional[datetime] = None
    snapshot_path = f"{path}.initial_review_snapshot"
    snapshot_required = {
        "snapshot_id",
        "initial_mode",
        "frozen_at",
        "review_sha256",
        "initial_report_label",
        "initial_report_sha256",
        "artifact_hashes",
        "recommendation",
        "confidence",
        "open_finding_ids",
    }
    snapshot = _object(log.get("initial_review_snapshot"), snapshot_path, issues, required=snapshot_required, allowed=snapshot_required)
    if snapshot is not None:
        snapshot_id = _nonempty_string(snapshot.get("snapshot_id"), f"{snapshot_path}.snapshot_id", issues)
        if snapshot_id is not None and not re.fullmatch(r"^S-[A-Za-z0-9._-]+$", snapshot_id):
            _add(issues, f"{snapshot_path}.snapshot_id", "id_format", "is not a valid snapshot identifier")
        frozen_at = _date_time(
            snapshot.get("frozen_at"), f"{snapshot_path}.frozen_at", issues
        )
        if frozen_at is not None:
            created_at = _date_time(root.get("created_at"), "$.created_at", issues)
            if created_at is not None and created_at > frozen_at:
                _add(
                    issues,
                    f"{snapshot_path}.frozen_at",
                    "freeze_order_conflict",
                    "must not predate the review bundle creation time",
                )
            for reviewer_index, reviewer in enumerate(root.get("reviewers", [])):
                if not isinstance(reviewer, dict) or reviewer.get("sealed_at") is None:
                    continue
                sealed_at = _date_time(
                    reviewer.get("sealed_at"),
                    f"$.reviewers[{reviewer_index}].sealed_at",
                    issues,
                )
                if sealed_at is not None and sealed_at > frozen_at:
                    _add(
                        issues,
                        f"{snapshot_path}.frozen_at",
                        "freeze_before_reviewer_seal",
                        f"must not predate reviewer {reviewer.get('id')!r} seal time",
                    )
            for evidence_time_path, supplied_at in evidence_supplied_times:
                if supplied_at < frozen_at:
                    _add(
                        issues,
                        evidence_time_path,
                        "pre_freeze_interaction_evidence",
                        "interaction evidence cannot be supplied before the initial review was frozen",
                    )
        _nonempty_string(
            snapshot.get("initial_report_label"),
            f"{snapshot_path}.initial_report_label",
            issues,
        )
        report_digest = _nonempty_string(
            snapshot.get("initial_report_sha256"),
            f"{snapshot_path}.initial_report_sha256",
            issues,
        )
        if report_digest is not None and not SHA256_RE.fullmatch(report_digest):
            _add(
                issues,
                f"{snapshot_path}.initial_report_sha256",
                "sha256",
                "must be 64 lowercase hexadecimal characters",
            )
        root_initial_report = root.get("initial_report")
        if isinstance(root_initial_report, dict):
            if snapshot.get("initial_report_label") != root_initial_report.get("label"):
                _add(
                    issues,
                    f"{snapshot_path}.initial_report_label",
                    "frozen_report_mismatch",
                    "must match the initial report label protected by the detached review digest",
                )
            if snapshot.get("initial_report_sha256") != root_initial_report.get("sha256"):
                _add(
                    issues,
                    f"{snapshot_path}.initial_report_sha256",
                    "frozen_report_mismatch",
                    "must match the initial report hash protected by the detached review digest",
                )
        initial_mode = _enum(
            snapshot.get("initial_mode"),
            f"{snapshot_path}.initial_mode",
            issues,
            MODES - {"interactive"},
        )
        _validate_mode_roles(initial_mode, root.get("reviewers"), issues)
        _validate_focus_scope(initial_mode, root, issues)
        _validate_focused_findings(initial_mode, root, findings, issues)
        _validate_re_review_context(
            initial_mode,
            root,
            findings,
            trusted_prior_review_sha256,
            trusted_prior_finding_ids,
            issues,
        )
        digest = _nonempty_string(snapshot.get("review_sha256"), f"{snapshot_path}.review_sha256", issues)
        if digest is not None and not SHA256_RE.fullmatch(digest):
            _add(issues, f"{snapshot_path}.review_sha256", "sha256", "must be 64 lowercase hexadecimal characters")
        elif digest is not None:
            expected_review_hash = canonical_initial_review_sha256(root, initial_mode)
            if digest != expected_review_hash:
                _add(
                    issues,
                    f"{snapshot_path}.review_sha256",
                    "frozen_review_hash_mismatch",
                    f"must equal the canonical initial-review hash {expected_review_hash}",
                )
        if trusted_initial_review_sha256 is None:
            _add(
                issues,
                f"{snapshot_path}.review_sha256",
                "untrusted_snapshot_digest",
                "interactive validation requires the detached digest retained before author interaction",
            )
        elif not SHA256_RE.fullmatch(trusted_initial_review_sha256):
            _add(
                issues,
                f"{snapshot_path}.review_sha256",
                "trusted_snapshot_digest_format",
                "the detached trusted digest must be 64 lowercase hexadecimal characters",
            )
        elif digest is not None and digest != trusted_initial_review_sha256:
            _add(
                issues,
                f"{snapshot_path}.review_sha256",
                "trusted_snapshot_mismatch",
                "does not match the detached digest retained before author interaction",
            )
        recommendation = _enum(snapshot.get("recommendation"), f"{snapshot_path}.recommendation", issues, DECISIONS)
        confidence = _confidence(snapshot.get("confidence"), f"{snapshot_path}.confidence", issues)
        if recommendation is not None and initial_recommendation is not None and recommendation != initial_recommendation:
            _add(issues, f"{snapshot_path}.recommendation", "frozen_review_mismatch", "must preserve the chair's initial recommendation")
        if confidence is not None and initial_confidence is not None and confidence != float(initial_confidence):
            _add(issues, f"{snapshot_path}.confidence", "frozen_review_mismatch", "must preserve the chair's initial confidence")
        hashes = _array(snapshot.get("artifact_hashes"), f"{snapshot_path}.artifact_hashes", issues, minimum=1)
        recorded_hashes: Dict[str, str] = {}
        if hashes is not None:
            for index, raw in enumerate(hashes):
                item_path = f"{snapshot_path}.artifact_hashes[{index}]"
                item = _object(raw, item_path, issues, required={"artifact_id", "sha256"}, allowed={"artifact_id", "sha256"})
                if item is None:
                    continue
                artifact_id = _identifier(item.get("artifact_id"), f"{item_path}.artifact_id", issues, "artifact")
                artifact_hash = _nonempty_string(item.get("sha256"), f"{item_path}.sha256", issues)
                if artifact_hash is not None and not SHA256_RE.fullmatch(artifact_hash):
                    _add(issues, f"{item_path}.sha256", "sha256", "must be 64 lowercase hexadecimal characters")
                if artifact_id is not None:
                    if artifact_id in recorded_hashes:
                        _add(issues, f"{item_path}.artifact_id", "duplicate_id", "duplicates an artifact hash record")
                    if artifact_hash is not None:
                        recorded_hashes[artifact_id] = artifact_hash
            if recorded_hashes != manifest_hashes:
                _add(issues, f"{snapshot_path}.artifact_hashes", "frozen_artifact_mismatch", "must exactly preserve every manifest artifact hash")
        open_ids = _array(snapshot.get("open_finding_ids"), f"{snapshot_path}.open_finding_ids", issues)
        checked_open: List[str] = []
        if open_ids is not None:
            for index, raw_id in enumerate(open_ids):
                finding_id = _identifier(raw_id, f"{snapshot_path}.open_finding_ids[{index}]", issues, "finding")
                if finding_id is not None:
                    checked_open.append(finding_id)
                    if finding_id not in findings:
                        _add(issues, f"{snapshot_path}.open_finding_ids[{index}]", "unknown_reference", "does not reference an initial finding")
            if len(checked_open) != len(set(checked_open)):
                _add(issues, f"{snapshot_path}.open_finding_ids", "duplicate_value", "must not repeat finding identifiers")
            if set(checked_open) != current_open:
                _add(issues, f"{snapshot_path}.open_finding_ids", "frozen_review_mismatch", "must equal the unchanged set of open initial findings")

    question_ids: Set[str] = set()
    question_findings: Dict[str, str] = {}
    question_rounds: Dict[str, int] = {}
    batch_rounds: Set[int] = set()
    batch_disclosures: Dict[int, str] = {}
    batch_issued_at: Dict[int, datetime] = {}
    batches_path = f"{path}.question_batches"
    batches = _array(log.get("question_batches"), batches_path, issues, minimum=1)
    if batches is not None:
        for batch_index, raw in enumerate(batches):
            batch_path = f"{batches_path}[{batch_index}]"
            batch_fields = {
                "round",
                "issued_at",
                "rationale",
                "disclosure_mode",
                "questions",
            }
            batch = _object(
                raw,
                batch_path,
                issues,
                required=batch_fields,
                allowed=batch_fields,
            )
            if batch is None:
                continue
            round_number = _integer(batch.get("round"), f"{batch_path}.round", issues, minimum=1)
            if round_number is not None:
                if round_number in batch_rounds:
                    _add(issues, f"{batch_path}.round", "duplicate_value", "must be unique")
                batch_rounds.add(round_number)
            issued_at = _date_time(
                batch.get("issued_at"), f"{batch_path}.issued_at", issues
            )
            if issued_at is not None:
                if frozen_at is not None and issued_at < frozen_at:
                    _add(
                        issues,
                        f"{batch_path}.issued_at",
                        "pre_freeze_question_batch",
                        "question batches cannot be issued before the initial review freeze",
                    )
                if round_number is not None:
                    batch_issued_at[round_number] = issued_at
            _nonempty_string(
                batch.get("rationale"), f"{batch_path}.rationale", issues
            )
            disclosure_mode = _enum(
                batch.get("disclosure_mode"),
                f"{batch_path}.disclosure_mode",
                issues,
                PRIVACY_MODES,
            )
            if (
                disclosure_mode is not None
                and privacy_mode is not None
                and PRIVACY_RANK[disclosure_mode] > PRIVACY_RANK[privacy_mode]
            ):
                _add(
                    issues,
                    f"{batch_path}.disclosure_mode",
                    "privacy_mode_conflict",
                    "question batch exceeds the bundle's authorized privacy mode",
                )
            if round_number is not None and disclosure_mode is not None:
                batch_disclosures[round_number] = disclosure_mode
            questions = _array(batch.get("questions"), f"{batch_path}.questions", issues, minimum=1)
            if questions is None:
                continue
            for question_index, raw_question in enumerate(questions):
                question_path = f"{batch_path}.questions[{question_index}]"
                fields = {
                    "id",
                    "finding_id",
                    "ambiguity",
                    "decision_relevance",
                    "requested_evidence",
                    "new_evidence_policy",
                    "evidence_treatment",
                }
                question = _object(raw_question, question_path, issues, required=fields, allowed=fields)
                if question is None:
                    continue
                question_id = _identifier(question.get("id"), f"{question_path}.id", issues, "question")
                finding_id = _identifier(question.get("finding_id"), f"{question_path}.finding_id", issues, "finding")
                if question_id is not None:
                    if question_id in question_ids:
                        _add(issues, f"{question_path}.id", "duplicate_id", "duplicates a question identifier")
                    question_ids.add(question_id)
                    if finding_id is not None:
                        question_findings[question_id] = finding_id
                    if round_number is not None:
                        question_rounds[question_id] = round_number
                if finding_id is not None and finding_id not in findings:
                    _add(issues, f"{question_path}.finding_id", "unknown_reference", "does not reference an initial finding")
                for key in (
                    "ambiguity",
                    "decision_relevance",
                    "requested_evidence",
                    "evidence_treatment",
                ):
                    _nonempty_string(question.get(key), f"{question_path}.{key}", issues)
                _enum(
                    question.get("new_evidence_policy"),
                    f"{question_path}.new_evidence_policy",
                    issues,
                    {"not_requested", "optional"},
                )

    if batch_rounds:
        expected_rounds = set(range(1, max(batch_rounds) + 1))
        if batch_rounds != expected_rounds:
            _add(
                issues,
                batches_path,
                "question_round_sequence",
                "question-batch rounds must be consecutive starting at 1",
            )
        prior_time: Optional[datetime] = None
        for round_number in sorted(batch_issued_at):
            issued_at = batch_issued_at[round_number]
            if prior_time is not None and issued_at < prior_time:
                _add(
                    issues,
                    f"{batches_path}[round={round_number}].issued_at",
                    "question_round_time_order",
                    "later rounds cannot be issued before earlier rounds",
                )
            prior_time = issued_at
        first_issued_at = batch_issued_at.get(1)
        if (
            interaction_type == "venue_rebuttal_simulation"
            and rules_verified_at is not None
            and first_issued_at is not None
            and rules_verified_at > first_issued_at
        ):
            _add(
                issues,
                f"{rules_path}.verified_at",
                "venue_rules_verified_too_late",
                "formal rebuttal rules must be verified before the first question batch is issued",
            )

    response_question_ids: Set[str] = set()
    response_categories: Dict[str, str] = {}
    response_evidence_ids: Set[str] = set()
    response_evidence_by_question: Dict[str, Set[str]] = {}
    response_received_at: Dict[str, datetime] = {}
    response_disclosure_limits: List[tuple[str, str, str]] = []
    responses_path = f"{path}.author_responses"
    responses = _array(log.get("author_responses"), responses_path, issues)
    if responses is not None:
        response_fields = {
            "question_id",
            "received_at",
            "primary_category",
            "response_text",
            "secondary_notes",
            "existing_location",
            "new_evidence_summary",
            "new_evidence_artifact_ids",
            "claim_scope_change",
            "planned_revision",
            "external_disclosure_limit",
            "confidentiality_restrictions",
        }
        for index, raw in enumerate(responses):
            item_path = f"{responses_path}[{index}]"
            response = _object(raw, item_path, issues, required=response_fields, allowed=response_fields)
            if response is None:
                continue
            question_id = _identifier(response.get("question_id"), f"{item_path}.question_id", issues, "question")
            if question_id is not None:
                if question_id not in question_ids:
                    _add(issues, f"{item_path}.question_id", "unknown_reference", "does not reference a logged question")
                if question_id in response_question_ids:
                    _add(issues, f"{item_path}.question_id", "duplicate_response", "has more than one primary response")
                response_question_ids.add(question_id)
            received_at = _date_time(
                response.get("received_at"), f"{item_path}.received_at", issues
            )
            if received_at is not None:
                if frozen_at is not None and received_at < frozen_at:
                    _add(
                        issues,
                        f"{item_path}.received_at",
                        "pre_freeze_author_response",
                        "author responses cannot predate the initial review freeze",
                    )
                if question_id is not None:
                    response_received_at[question_id] = received_at
                    response_round = question_rounds.get(question_id)
                    question_issued_at = batch_issued_at.get(response_round or -1)
                    if question_issued_at is not None and received_at < question_issued_at:
                        _add(
                            issues,
                            f"{item_path}.received_at",
                            "response_before_question",
                            "author response cannot predate its question batch",
                        )
            category = _enum(
                response.get("primary_category"),
                f"{item_path}.primary_category",
                issues,
                ANSWER_CATEGORIES,
            )
            if question_id is not None and category is not None and question_id not in response_categories:
                response_categories[question_id] = category
            _nonempty_string(response.get("response_text"), f"{item_path}.response_text", issues)
            _validate_string_array(
                response.get("secondary_notes"), f"{item_path}.secondary_notes", issues
            )
            for key in (
                "existing_location",
                "new_evidence_summary",
                "claim_scope_change",
                "planned_revision",
            ):
                if response.get(key) is not None:
                    _nonempty_string(response.get(key), f"{item_path}.{key}", issues)
            response_evidence = _array(
                response.get("new_evidence_artifact_ids"),
                f"{item_path}.new_evidence_artifact_ids",
                issues,
            )
            checked_response_evidence: List[str] = []
            if response_evidence is not None:
                for evidence_index, raw_evidence_id in enumerate(response_evidence):
                    evidence_id = _identifier(
                        raw_evidence_id,
                        f"{item_path}.new_evidence_artifact_ids[{evidence_index}]",
                        issues,
                        "evidence",
                    )
                    if evidence_id is not None:
                        checked_response_evidence.append(evidence_id)
                        response_evidence_ids.add(evidence_id)
                        if evidence_id not in evidence_ids:
                            _add(
                                issues,
                                f"{item_path}.new_evidence_artifact_ids[{evidence_index}]",
                                "unknown_reference",
                                "does not reference a logged interaction-evidence artifact",
                            )
                if len(checked_response_evidence) != len(set(checked_response_evidence)):
                    _add(
                        issues,
                        f"{item_path}.new_evidence_artifact_ids",
                        "duplicate_value",
                        "must not repeat evidence identifiers",
                    )
            if question_id is not None:
                response_evidence_by_question[question_id] = set(
                    checked_response_evidence
                )
                if received_at is not None:
                    for evidence_id in checked_response_evidence:
                        supplied_at = evidence_supplied_at.get(evidence_id)
                        if supplied_at is not None and supplied_at > received_at:
                            _add(
                                issues,
                                f"{item_path}.new_evidence_artifact_ids",
                                "evidence_after_response",
                                f"evidence {evidence_id!r} was supplied after the response that cites it",
                            )
            _nonempty_string(response.get("confidentiality_restrictions"), f"{item_path}.confidentiality_restrictions", issues)
            disclosure_limit = _enum(
                response.get("external_disclosure_limit"),
                f"{item_path}.external_disclosure_limit",
                issues,
                PRIVACY_MODES,
            )
            if question_id is not None and disclosure_limit is not None:
                effective_limit = disclosure_limit
                for evidence_id in checked_response_evidence:
                    evidence_limit = evidence_disclosure_limits.get(evidence_id)
                    if (
                        evidence_limit is not None
                        and PRIVACY_RANK[evidence_limit] < PRIVACY_RANK[effective_limit]
                    ):
                        effective_limit = evidence_limit
                response_disclosure_limits.append(
                    (question_id, effective_limit, item_path)
                )
            category_evidence_field = {
                "already_supported_clarification": "existing_location",
                "new_unpublished_evidence": "new_evidence_summary",
                "planned_revision": "planned_revision",
                "concession_or_scope_narrowing": "claim_scope_change",
            }.get(category or "")
            if category_evidence_field is not None and response.get(category_evidence_field) is None:
                _add(
                    issues,
                    f"{item_path}.{category_evidence_field}",
                    "response_evidence_missing",
                    f"is required for response category {category}",
                )
            if category == "new_unpublished_evidence" and not checked_response_evidence:
                _add(
                    issues,
                    f"{item_path}.new_evidence_artifact_ids",
                    "response_evidence_missing",
                    "new unpublished evidence must be represented by at least one hashed evidence artifact",
                )

    for question_id, received_at in response_received_at.items():
        response_round = question_rounds.get(question_id)
        if response_round is None:
            continue
        for later_round, issued_at in batch_issued_at.items():
            if later_round > response_round and issued_at < received_at:
                _add(
                    issues,
                    f"{batches_path}[round={later_round}].issued_at",
                    "next_round_before_response",
                    f"round {later_round} cannot predate the recorded response to {question_id}",
                )

    for question_id, disclosure_limit, response_path in response_disclosure_limits:
        response_round = question_rounds.get(question_id)
        if response_round is None:
            continue
        for batch_round, later_disclosure in sorted(batch_disclosures.items()):
            if (
                batch_round > response_round
                and PRIVACY_RANK[later_disclosure] > PRIVACY_RANK[disclosure_limit]
            ):
                _add(
                    issues,
                    f"$.interaction_log.question_batches[round={batch_round}].disclosure_mode",
                    "response_privacy_override",
                    f"later round exceeds the disclosure limit recorded at {response_path}",
                )

    post_freeze_ids: Set[str] = set()
    post_freeze_evidence_ids: Set[str] = set()
    post_freeze_statuses: Dict[str, str] = {}
    post_freeze_effective_severities: Dict[str, Optional[str]] = {}
    post_freeze_verification_statuses: Dict[str, str] = {}
    post_freeze_path = f"{path}.post_freeze_findings"
    post_freeze_findings = _array(
        log.get("post_freeze_findings"), post_freeze_path, issues
    )
    if post_freeze_findings is not None:
        post_freeze_fields = {
            "id",
            "origin",
            "reviewer_id",
            "verifier_id",
            "verification_status",
            "verified_severity",
            "checked_evidence",
            "verification_performed_at",
            "verification_report_sha256",
            "verification_rationale",
            "category",
            "severity",
            "confidence",
            "conditional",
            "status",
            "observation",
            "rationale_not_in_initial_review",
            "evidence_artifact_ids",
            "linked_initial_finding_ids",
        }
        input_scope = root.get("input_scope")
        complete_input = bool(
            isinstance(input_scope, dict)
            and input_scope.get("material_scope") == "full_manuscript"
            and input_scope.get("complete_relevant_artifact_inspected") is True
        )
        for index, raw in enumerate(post_freeze_findings):
            item_path = f"{post_freeze_path}[{index}]"
            post_finding = _object(
                raw,
                item_path,
                issues,
                required=post_freeze_fields,
                allowed=post_freeze_fields,
            )
            if post_finding is None:
                continue
            post_id = _identifier(
                post_finding.get("id"),
                f"{item_path}.id",
                issues,
                "post_freeze_finding",
            )
            if post_id is not None:
                if post_id in post_freeze_ids:
                    _add(
                        issues,
                        f"{item_path}.id",
                        "duplicate_id",
                        "duplicates a post-freeze finding identifier",
                    )
                post_freeze_ids.add(post_id)

            origin_path = f"{item_path}.origin"
            origin = _object(
                post_finding.get("origin"),
                origin_path,
                issues,
                required={"label", "round", "question_id"},
                allowed={"label", "round", "question_id"},
            )
            origin_question_id: Optional[str] = None
            if origin is not None:
                _enum(
                    origin.get("label"),
                    f"{origin_path}.label",
                    issues,
                    POST_FREEZE_FINDING_ORIGINS,
                )
                origin_round = _integer(
                    origin.get("round"), f"{origin_path}.round", issues, minimum=1
                )
                origin_question_id = _identifier(
                    origin.get("question_id"),
                    f"{origin_path}.question_id",
                    issues,
                    "question",
                )
                if (
                    origin_question_id is not None
                    and origin_question_id not in response_question_ids
                ):
                    _add(
                        issues,
                        f"{origin_path}.question_id",
                        "post_freeze_trigger_unanswered",
                        "must reference a question with an actual author response",
                    )
                if (
                    origin_question_id is not None
                    and origin_round is not None
                    and question_rounds.get(origin_question_id) != origin_round
                ):
                    _add(
                        issues,
                        f"{origin_path}.round",
                        "post_freeze_origin_round_mismatch",
                        "must match the round containing the triggering question",
                    )

            reviewer_id = _identifier(
                post_finding.get("reviewer_id"),
                f"{item_path}.reviewer_id",
                issues,
                "reviewer",
            )
            if reviewer_id is not None and reviewer_id not in reviewer_records:
                _add(
                    issues,
                    f"{item_path}.reviewer_id",
                    "unknown_reference",
                    "does not reference a declared reviewer",
                )
            verifier_raw = post_finding.get("verifier_id")
            verifier_id: Optional[str] = None
            if verifier_raw is not None:
                verifier_id = _identifier(
                    verifier_raw,
                    f"{item_path}.verifier_id",
                    issues,
                    "reviewer",
                )
                if verifier_id is not None and verifier_id not in reviewer_records:
                    _add(
                        issues,
                        f"{item_path}.verifier_id",
                        "unknown_reference",
                        "does not reference a declared reviewer",
                    )
                if verifier_id is not None and verifier_id == reviewer_id:
                    _add(
                        issues,
                        f"{item_path}.verifier_id",
                        "post_freeze_self_verification",
                        "must differ from the post-freeze finding originator",
                    )
            verification_status = _enum(
                post_finding.get("verification_status"),
                f"{item_path}.verification_status",
                issues,
                POST_FREEZE_VERIFICATION_STATES,
            )
            if post_id is not None and verification_status is not None:
                post_freeze_verification_statuses[post_id] = verification_status
            verified_severity_raw = post_finding.get("verified_severity")
            verified_severity: Optional[str] = None
            if verified_severity_raw is not None:
                verified_severity = _enum(
                    verified_severity_raw,
                    f"{item_path}.verified_severity",
                    issues,
                    SEVERITIES,
                )
            checked_evidence = _boolean(
                post_finding.get("checked_evidence"),
                f"{item_path}.checked_evidence",
                issues,
            )
            verification_performed_at_raw = post_finding.get(
                "verification_performed_at"
            )
            verification_performed_at: Optional[datetime] = None
            if verification_performed_at_raw is not None:
                verification_performed_at = _date_time(
                    verification_performed_at_raw,
                    f"{item_path}.verification_performed_at",
                    issues,
                )
            verification_report_raw = post_finding.get(
                "verification_report_sha256"
            )
            verification_report: Optional[str] = None
            if verification_report_raw is not None:
                verification_report = _nonempty_string(
                    verification_report_raw,
                    f"{item_path}.verification_report_sha256",
                    issues,
                )
                if (
                    verification_report is not None
                    and not SHA256_RE.fullmatch(verification_report)
                ):
                    _add(
                        issues,
                        f"{item_path}.verification_report_sha256",
                        "sha256",
                        "must be 64 lowercase hexadecimal characters",
                    )
            _nonempty_string(
                post_finding.get("verification_rationale"),
                f"{item_path}.verification_rationale",
                issues,
            )
            severity = _enum(
                post_finding.get("severity"),
                f"{item_path}.severity",
                issues,
                SEVERITIES,
            )
            if verification_status == "not_required":
                if verifier_id is not None:
                    _add(
                        issues,
                        f"{item_path}.verifier_id",
                        "post_freeze_verification_conflict",
                        "must be null when verification_status is not_required",
                    )
                if checked_evidence is not False:
                    _add(
                        issues,
                        f"{item_path}.checked_evidence",
                        "post_freeze_verification_conflict",
                        "must be false when verification_status is not_required",
                    )
                if verification_performed_at_raw is not None:
                    _add(
                        issues,
                        f"{item_path}.verification_performed_at",
                        "post_freeze_verification_conflict",
                        "must be null when verification_status is not_required",
                    )
                if verification_report_raw is not None:
                    _add(
                        issues,
                        f"{item_path}.verification_report_sha256",
                        "post_freeze_verification_conflict",
                        "must be null when verification_status is not_required",
                    )
                if verified_severity_raw is not None:
                    _add(
                        issues,
                        f"{item_path}.verified_severity",
                        "post_freeze_verification_conflict",
                        "must be null when verification_status is not_required",
                    )
            elif verification_status is not None:
                if verifier_id is None:
                    _add(
                        issues,
                        f"{item_path}.verifier_id",
                        "missing_post_freeze_verification",
                        "a post-freeze verification outcome requires a distinct verifier",
                    )
                if checked_evidence is not True:
                    _add(
                        issues,
                        f"{item_path}.checked_evidence",
                        "missing_post_freeze_verification",
                        "post-freeze verification must check the linked evidence",
                    )
                if verification_performed_at is None:
                    _add(
                        issues,
                        f"{item_path}.verification_performed_at",
                        "missing_post_freeze_verification",
                        "post-freeze verification requires its interaction-specific completion time",
                    )
                if verification_report is None:
                    _add(
                        issues,
                        f"{item_path}.verification_report_sha256",
                        "missing_post_freeze_verification",
                        "post-freeze verification requires an interaction-specific report hash",
                    )
                elif verifier_id is not None:
                    verifier_initial_hash = reviewer_records.get(verifier_id, {}).get(
                        "report_sha256"
                    )
                    if verification_report == verifier_initial_hash:
                        _add(
                            issues,
                            f"{item_path}.verification_report_sha256",
                            "reused_initial_verifier_seal",
                            "must differ from the verifier's pre-interaction report hash",
                        )

            if severity == "critical":
                if verification_status in {None, "not_required"}:
                    _add(
                        issues,
                        f"{item_path}.verification_status",
                        "missing_post_freeze_verification",
                        "Critical post-freeze findings require an interaction-scoped verification outcome",
                    )
                if verifier_id is not None:
                    verifier = reviewer_records.get(verifier_id, {})
                    if verifier.get("role") != "critical_verifier":
                        _add(
                            issues,
                            f"{item_path}.verifier_id",
                            "post_freeze_verifier_role",
                            "Critical post-freeze findings require the declared critical_verifier role",
                        )
                    if verifier.get("sealed") is not True:
                        _add(
                            issues,
                            f"{item_path}.verifier_id",
                            "unsealed_post_freeze_verifier",
                            "Critical post-freeze verifier must have a sealed reviewer record",
                        )

            if verification_status == "confirmed":
                if severity is not None and verified_severity != severity:
                    _add(
                        issues,
                        f"{item_path}.verified_severity",
                        "post_freeze_verification_conflict",
                        "confirmed verification must preserve the declared severity",
                    )
            elif verification_status == "downgraded":
                if (
                    severity is None
                    or verified_severity is None
                    or SEVERITY_RANK[verified_severity] >= SEVERITY_RANK[severity]
                ):
                    _add(
                        issues,
                        f"{item_path}.verified_severity",
                        "post_freeze_verification_conflict",
                        "downgraded verification requires a strictly lower verified severity",
                    )
            elif verification_status in {"resolved", "withdrawn", "unresolved"}:
                if verified_severity_raw is not None:
                    _add(
                        issues,
                        f"{item_path}.verified_severity",
                        "post_freeze_verification_conflict",
                        f"must be null when verification_status is {verification_status}",
                    )

            _enum(
                post_finding.get("category"),
                f"{item_path}.category",
                issues,
                CATEGORIES,
            )
            _confidence(
                post_finding.get("confidence"), f"{item_path}.confidence", issues
            )
            conditional = _boolean(
                post_finding.get("conditional"),
                f"{item_path}.conditional",
                issues,
            )
            if not complete_input and conditional is False:
                _add(
                    issues,
                    f"{item_path}.conditional",
                    "partial_input_finding",
                    "post-freeze findings must be conditional when the inspected input is incomplete",
                )
            status = _enum(
                post_finding.get("status"),
                f"{item_path}.status",
                issues,
                FINDING_STATES,
            )
            if post_id is not None and status is not None:
                post_freeze_statuses[post_id] = status
            expected_lifecycle = {
                "not_required": "open",
                "confirmed": "open",
                "downgraded": "open",
                "unresolved": "open",
                "resolved": "resolved",
                "withdrawn": "withdrawn",
            }.get(verification_status or "")
            if (
                status is not None
                and expected_lifecycle is not None
                and status != expected_lifecycle
            ):
                _add(
                    issues,
                    f"{item_path}.status",
                    "post_freeze_status_conflict",
                    f"verification_status {verification_status} requires lifecycle status {expected_lifecycle}",
                )
            if post_id is not None:
                effective_severity: Optional[str] = None
                if status == "open":
                    effective_severity = (
                        verified_severity
                        if verification_status == "downgraded"
                        else severity
                    )
                post_freeze_effective_severities[post_id] = effective_severity
            for key in ("observation", "rationale_not_in_initial_review"):
                _nonempty_string(
                    post_finding.get(key), f"{item_path}.{key}", issues
                )

            evidence_values = _array(
                post_finding.get("evidence_artifact_ids"),
                f"{item_path}.evidence_artifact_ids",
                issues,
                minimum=1,
            )
            checked_evidence_ids: List[str] = []
            if evidence_values is not None:
                for evidence_index, raw_evidence_id in enumerate(evidence_values):
                    evidence_id = _identifier(
                        raw_evidence_id,
                        f"{item_path}.evidence_artifact_ids[{evidence_index}]",
                        issues,
                        "evidence",
                    )
                    if evidence_id is not None:
                        checked_evidence_ids.append(evidence_id)
                        post_freeze_evidence_ids.add(evidence_id)
                        if evidence_id not in evidence_ids:
                            _add(
                                issues,
                                f"{item_path}.evidence_artifact_ids[{evidence_index}]",
                                "unknown_reference",
                                "does not reference logged post-freeze evidence",
                            )
                if len(checked_evidence_ids) != len(set(checked_evidence_ids)):
                    _add(
                        issues,
                        f"{item_path}.evidence_artifact_ids",
                        "duplicate_value",
                        "must not repeat interaction-evidence identifiers",
                    )
                if origin_question_id is not None and not set(
                    checked_evidence_ids
                ).issubset(response_evidence_by_question.get(origin_question_id, set())):
                    _add(
                        issues,
                        f"{item_path}.evidence_artifact_ids",
                        "post_freeze_evidence_origin_mismatch",
                        "must be a subset of evidence linked by the triggering author response",
                    )
            if verification_performed_at is not None:
                if frozen_at is not None and verification_performed_at < frozen_at:
                    _add(
                        issues,
                        f"{item_path}.verification_performed_at",
                        "pre_freeze_post_freeze_verification",
                        "post-freeze verification cannot predate the initial review freeze",
                    )
                triggering_response_at = response_received_at.get(
                    origin_question_id or ""
                )
                if (
                    triggering_response_at is not None
                    and verification_performed_at <= triggering_response_at
                ):
                    _add(
                        issues,
                        f"{item_path}.verification_performed_at",
                        "post_freeze_verification_time_order",
                        "must be later than the triggering author response",
                    )
                for evidence_id in checked_evidence_ids:
                    supplied_at = evidence_supplied_at.get(evidence_id)
                    if (
                        supplied_at is not None
                        and verification_performed_at <= supplied_at
                    ):
                        _add(
                            issues,
                            f"{item_path}.verification_performed_at",
                            "post_freeze_verification_time_order",
                            f"must be later than linked evidence {evidence_id}",
                        )

            linked_values = _array(
                post_finding.get("linked_initial_finding_ids"),
                f"{item_path}.linked_initial_finding_ids",
                issues,
            )
            checked_linked: List[str] = []
            if linked_values is not None:
                for linked_index, raw_finding_id in enumerate(linked_values):
                    linked_id = _identifier(
                        raw_finding_id,
                        f"{item_path}.linked_initial_finding_ids[{linked_index}]",
                        issues,
                        "finding",
                    )
                    if linked_id is not None:
                        checked_linked.append(linked_id)
                        if linked_id not in findings:
                            _add(
                                issues,
                                f"{item_path}.linked_initial_finding_ids[{linked_index}]",
                                "unknown_reference",
                                "does not reference a frozen initial finding",
                            )
                if len(checked_linked) != len(set(checked_linked)):
                    _add(
                        issues,
                        f"{item_path}.linked_initial_finding_ids",
                        "duplicate_value",
                        "must not repeat initial finding identifiers",
                    )

    reevaluation_question_ids: Set[str] = set()
    reevaluation_statuses: Dict[str, Set[str]] = {}
    updated_severities: Dict[str, Set[str]] = {}
    required_dependency_ids: Set[str] = set()
    reevaluations_path = f"{path}.re_evaluations"
    reevaluations = _array(log.get("re_evaluations"), reevaluations_path, issues)
    if reevaluations is not None:
        reevaluation_fields = {"question_id", "finding_id", "evaluator_reviewer_id", "status", "verification_performed", "original_severity", "updated_severity", "original_confidence", "updated_confidence", "rationale", "required_manuscript_action"}
        for index, raw in enumerate(reevaluations):
            item_path = f"{reevaluations_path}[{index}]"
            reevaluation = _object(raw, item_path, issues, required=reevaluation_fields, allowed=reevaluation_fields)
            if reevaluation is None:
                continue
            question_id = _identifier(reevaluation.get("question_id"), f"{item_path}.question_id", issues, "question")
            finding_id = _identifier(reevaluation.get("finding_id"), f"{item_path}.finding_id", issues, "finding")
            evaluator_id = _identifier(
                reevaluation.get("evaluator_reviewer_id"),
                f"{item_path}.evaluator_reviewer_id",
                issues,
                "reviewer",
            )
            if evaluator_id is not None and evaluator_id not in reviewer_records:
                _add(
                    issues,
                    f"{item_path}.evaluator_reviewer_id",
                    "unknown_reference",
                    "does not reference a declared reviewer",
                )
            status = _enum(reevaluation.get("status"), f"{item_path}.status", issues, REEVALUATION_STATES)
            if question_id is not None:
                if question_id not in response_question_ids:
                    _add(issues, f"{item_path}.question_id", "missing_response", "must follow a logged author response")
                if question_id in reevaluation_question_ids:
                    _add(issues, f"{item_path}.question_id", "duplicate_reevaluation", "has more than one re-evaluation")
                reevaluation_question_ids.add(question_id)
                if finding_id is not None and question_findings.get(question_id) != finding_id:
                    _add(issues, f"{item_path}.finding_id", "question_finding_mismatch", "must match the finding linked by the question")
                category = response_categories.get(question_id)
                if (
                    category is not None
                    and status is not None
                    and status not in ANSWER_STATUS_COMPATIBILITY[category]
                ):
                    _add(
                        issues,
                        f"{item_path}.status",
                        "answer_status_conflict",
                        f"status {status!r} is incompatible with response category {category!r}",
                    )
                if status == "new_evidence_requires_inclusion":
                    required_dependency_ids.update(
                        response_evidence_by_question.get(question_id, set())
                    )
            finding = findings.get(finding_id) if finding_id is not None else None
            if finding is None and finding_id is not None:
                _add(issues, f"{item_path}.finding_id", "unknown_reference", "does not reference an initial finding")
            elif finding is not None:
                original_severity = _enum(reevaluation.get("original_severity"), f"{item_path}.original_severity", issues, SEVERITIES)
                original_confidence = _confidence(reevaluation.get("original_confidence"), f"{item_path}.original_confidence", issues)
                if original_severity is not None and original_severity != finding.get("severity"):
                    _add(issues, f"{item_path}.original_severity", "frozen_review_mismatch", "must preserve the initial finding severity")
                if original_confidence is not None and original_confidence != float(finding.get("confidence")):
                    _add(issues, f"{item_path}.original_confidence", "frozen_review_mismatch", "must preserve the initial finding confidence")
            updated_severity = reevaluation.get("updated_severity")
            checked_updated_severity: Optional[str] = None
            if updated_severity is not None:
                checked_updated_severity = _enum(
                    updated_severity,
                    f"{item_path}.updated_severity",
                    issues,
                    SEVERITIES,
                )
            _confidence(reevaluation.get("updated_confidence"), f"{item_path}.updated_confidence", issues)
            for key in ("verification_performed", "rationale", "required_manuscript_action"):
                _nonempty_string(reevaluation.get(key), f"{item_path}.{key}", issues)
            if finding_id is not None and status is not None:
                reevaluation_statuses.setdefault(finding_id, set()).add(status)
            if finding_id is not None and checked_updated_severity is not None:
                updated_severities.setdefault(finding_id, set()).add(
                    checked_updated_severity
                )
    for question_id in sorted(response_question_ids - reevaluation_question_ids):
        _add(issues, reevaluations_path, "missing_reevaluation", f"response to {question_id!r} requires a re-evaluation")
    for finding_id, severities in sorted(updated_severities.items()):
        if len(severities) > 1:
            _add(
                issues,
                reevaluations_path,
                "updated_severity_conflict",
                f"re-evaluations for {finding_id!r} disagree on updated severity: "
                + ", ".join(sorted(severities)),
            )

    if interaction_phase == "awaiting_author_response":
        if question_ids and question_ids <= response_question_ids:
            _add(
                issues,
                f"{path}.interaction_phase",
                "awaiting_without_pending_question",
                "awaiting_author_response requires at least one unanswered question",
            )
        if not response_question_ids:
            if evidence_ids:
                _add(
                    issues,
                    evidence_path,
                    "prefilled_interaction_record",
                    "first-turn awaiting state cannot contain post-freeze evidence before an author response",
                )
            if reevaluation_question_ids:
                _add(
                    issues,
                    reevaluations_path,
                    "prefilled_interaction_record",
                    "first-turn awaiting state cannot contain re-evaluations before an author response",
                )
            if post_freeze_ids:
                _add(
                    issues,
                    post_freeze_path,
                    "prefilled_interaction_record",
                    "first-turn awaiting state cannot contain post-freeze findings before an author response",
                )
            if "revised_provisional_meta_review" in log:
                _add(
                    issues,
                    f"{path}.revised_provisional_meta_review",
                    "prefilled_interaction_record",
                    "first-turn awaiting state cannot contain a revised meta-review",
                )
    elif interaction_phase == "completed":
        if not response_question_ids:
            _add(
                issues,
                responses_path,
                "completed_without_response",
                "completed interaction requires at least one actual author response",
            )
        if not reevaluation_question_ids:
            _add(
                issues,
                reevaluations_path,
                "completed_without_reevaluation",
                "completed interaction requires at least one response-linked re-evaluation",
            )
        if "revised_provisional_meta_review" not in log:
            _add(
                issues,
                f"{path}.revised_provisional_meta_review",
                "required",
                "is required when interaction_phase is completed",
            )

    meta_path = f"{path}.revised_provisional_meta_review"
    meta_fields = {"initial_recommendation", "updated_provisional_recommendation", "updated_confidence", "judgment_scope", "resolved_finding_ids", "remaining_finding_ids", "disputed_finding_ids", "post_freeze_finding_treatments", "new_evidence_dependency_ids", "limitations", "rationale"}
    meta = None
    if "revised_provisional_meta_review" in log:
        meta = _object(log.get("revised_provisional_meta_review"), meta_path, issues, required=meta_fields, allowed=meta_fields)
    if meta is not None:
        meta_initial = _enum(meta.get("initial_recommendation"), f"{meta_path}.initial_recommendation", issues, DECISIONS)
        updated = _enum(meta.get("updated_provisional_recommendation"), f"{meta_path}.updated_provisional_recommendation", issues, DECISIONS)
        input_scope = root.get("input_scope")
        if isinstance(input_scope, dict):
            material_scope = input_scope.get("material_scope")
            complete = input_scope.get("complete_relevant_artifact_inspected")
            if (
                not (
                    material_scope == "full_manuscript"
                    and complete is True
                )
                and updated not in {None, "no_recommendation"}
            ):
                _add(
                    issues,
                    f"{meta_path}.updated_provisional_recommendation",
                    "partial_input_decision",
                    "interaction cannot convert incomplete manuscript inspection into a whole-paper verdict",
                )
        if meta_initial is not None and meta_initial != initial_recommendation:
            _add(issues, f"{meta_path}.initial_recommendation", "frozen_review_mismatch", "must preserve the initial chair recommendation")
        _confidence(meta.get("updated_confidence"), f"{meta_path}.updated_confidence", issues)
        judgment_scope = _enum(meta.get("judgment_scope"), f"{meta_path}.judgment_scope", issues, {"frozen_manuscript", "hypothetical_revision", "revised_manuscript"})
        classification: Dict[str, Set[str]] = {}
        for key in ("resolved_finding_ids", "remaining_finding_ids", "disputed_finding_ids"):
            values = _array(meta.get(key), f"{meta_path}.{key}", issues)
            checked: List[str] = []
            if values is not None:
                for index, raw_id in enumerate(values):
                    if isinstance(raw_id, str) and raw_id.startswith("PF-"):
                        _add(
                            issues,
                            f"{meta_path}.{key}[{index}]",
                            "post_freeze_finding_fold",
                            "post-freeze PF-* findings must be treated separately from frozen initial findings",
                        )
                    finding_id = _identifier(raw_id, f"{meta_path}.{key}[{index}]", issues, "finding")
                    if finding_id is not None:
                        checked.append(finding_id)
                        if finding_id not in findings:
                            _add(issues, f"{meta_path}.{key}[{index}]", "unknown_reference", "does not reference an initial finding")
                if len(checked) != len(set(checked)):
                    _add(issues, f"{meta_path}.{key}", "duplicate_value", "must not repeat finding identifiers")
            classification[key] = set(checked)
        overlap = (classification["resolved_finding_ids"] & classification["remaining_finding_ids"]) | (classification["resolved_finding_ids"] & classification["disputed_finding_ids"]) | (classification["remaining_finding_ids"] & classification["disputed_finding_ids"])
        if overlap:
            _add(issues, meta_path, "classification_overlap", "finding classifications must be disjoint: " + ", ".join(sorted(overlap)))
        if set().union(*classification.values()) != current_open:
            _add(issues, meta_path, "classification_coverage", "resolved, remaining, and disputed IDs must classify every frozen open finding exactly once")
        expected_resolved: Set[str] = set()
        expected_disputed: Set[str] = set()
        expected_remaining: Set[str] = set()
        for finding_id in current_open:
            linked_questions = {
                question_id
                for question_id, linked_finding in question_findings.items()
                if linked_finding == finding_id
            }
            statuses = reevaluation_statuses.get(finding_id, set())
            complete = bool(linked_questions) and linked_questions <= reevaluation_question_ids
            if complete and statuses == {"resolved_in_manuscript"}:
                expected_resolved.add(finding_id)
            elif (
                complete
                and "disputed" in statuses
                and statuses <= {"resolved_in_manuscript", "disputed"}
            ):
                expected_disputed.add(finding_id)
            else:
                expected_remaining.add(finding_id)

        expected_classification = {
            "resolved_finding_ids": expected_resolved,
            "remaining_finding_ids": expected_remaining,
            "disputed_finding_ids": expected_disputed,
        }
        for key, expected_ids in expected_classification.items():
            if classification[key] != expected_ids:
                _add(
                    issues,
                    f"{meta_path}.{key}",
                    "resolution_status_conflict",
                    "must equal the deterministic classification: "
                    + ", ".join(sorted(expected_ids)),
                )

        treatment_path = f"{meta_path}.post_freeze_finding_treatments"
        treatments = _array(
            meta.get("post_freeze_finding_treatments"), treatment_path, issues
        )
        treated_ids: List[str] = []
        if treatments is not None:
            treatment_fields = {"finding_id", "treatment", "rationale"}
            for index, raw_treatment in enumerate(treatments):
                item_path = f"{treatment_path}[{index}]"
                treatment_record = _object(
                    raw_treatment,
                    item_path,
                    issues,
                    required=treatment_fields,
                    allowed=treatment_fields,
                )
                if treatment_record is None:
                    continue
                post_id = _identifier(
                    treatment_record.get("finding_id"),
                    f"{item_path}.finding_id",
                    issues,
                    "post_freeze_finding",
                )
                treatment = _enum(
                    treatment_record.get("treatment"),
                    f"{item_path}.treatment",
                    issues,
                    POST_FREEZE_META_TREATMENTS,
                )
                _nonempty_string(
                    treatment_record.get("rationale"),
                    f"{item_path}.rationale",
                    issues,
                )
                if post_id is not None:
                    treated_ids.append(post_id)
                    if post_id not in post_freeze_ids:
                        _add(
                            issues,
                            f"{item_path}.finding_id",
                            "unknown_reference",
                            "does not reference a declared post-freeze finding",
                        )
                    lifecycle = post_freeze_statuses.get(post_id)
                    verification = post_freeze_verification_statuses.get(post_id)
                    if (
                        treatment == "withdrawn_after_verification"
                        and lifecycle != "withdrawn"
                    ):
                        _add(
                            issues,
                            f"{item_path}.treatment",
                            "post_freeze_treatment_conflict",
                            "withdrawn_after_verification requires lifecycle status withdrawn",
                        )
                    if (
                        lifecycle == "withdrawn"
                        and treatment != "withdrawn_after_verification"
                    ):
                        _add(
                            issues,
                            f"{item_path}.treatment",
                            "post_freeze_treatment_conflict",
                            "withdrawn post-freeze findings require withdrawn_after_verification treatment",
                        )
                    if (
                        lifecycle == "resolved"
                        and treatment
                        not in {
                            "affects_provisional_recommendation",
                            "documented_no_recommendation_change",
                        }
                    ):
                        _add(
                            issues,
                            f"{item_path}.treatment",
                            "post_freeze_treatment_conflict",
                            "resolved post-freeze findings must be recorded as affecting or not changing the provisional recommendation",
                        )
                    if (
                        lifecycle == "open"
                        and treatment == "withdrawn_after_verification"
                    ):
                        _add(
                            issues,
                            f"{item_path}.treatment",
                            "post_freeze_treatment_conflict",
                            "open post-freeze findings cannot use withdrawn treatment",
                        )
                    if (
                        verification == "unresolved"
                        and treatment == "affects_provisional_recommendation"
                    ):
                        _add(
                            issues,
                            f"{item_path}.treatment",
                            "unresolved_post_freeze_affects_decision",
                            "an unresolved verification cannot be represented as a verified recommendation driver; defer or document it instead",
                        )
            if len(treated_ids) != len(set(treated_ids)):
                _add(
                    issues,
                    treatment_path,
                    "duplicate_value",
                    "must not repeat post-freeze finding identifiers",
                )
            if set(treated_ids) != post_freeze_ids:
                _add(
                    issues,
                    treatment_path,
                    "post_freeze_treatment_coverage",
                    "must treat every post-freeze finding exactly once",
                )

        effective_open_critical: Set[str] = set()
        for finding_id in current_open - expected_resolved:
            severity_values = {str(findings[finding_id].get("severity"))}
            severity_values.update(updated_severities.get(finding_id, set()))
            if any(SEVERITY_RANK.get(value, 0) == SEVERITY_RANK["critical"] for value in severity_values):
                effective_open_critical.add(finding_id)
        if updated in ACCEPTING_DECISIONS and effective_open_critical:
            _add(issues, f"{meta_path}.updated_provisional_recommendation", "critical_accept_conflict", "cannot recommend acceptance while critical findings remain unresolved after interaction")
        open_critical_post_freeze = {
            post_id
            for post_id, severity in post_freeze_effective_severities.items()
            if severity == "critical"
        }
        if updated in ACCEPTING_DECISIONS and open_critical_post_freeze:
            _add(
                issues,
                f"{meta_path}.updated_provisional_recommendation",
                "post_freeze_critical_accept_conflict",
                "cannot recommend acceptance while an effective Critical post-freeze finding remains after verification",
            )
        required_dependency_ids.update(post_freeze_evidence_ids)
        dependencies = _array(
            meta.get("new_evidence_dependency_ids"),
            f"{meta_path}.new_evidence_dependency_ids",
            issues,
        )
        checked_dependencies: List[str] = []
        if dependencies is not None:
            for index, raw_evidence_id in enumerate(dependencies):
                evidence_id = _identifier(
                    raw_evidence_id,
                    f"{meta_path}.new_evidence_dependency_ids[{index}]",
                    issues,
                    "evidence",
                )
                if evidence_id is not None:
                    checked_dependencies.append(evidence_id)
                    if evidence_id not in evidence_ids:
                        _add(
                            issues,
                            f"{meta_path}.new_evidence_dependency_ids[{index}]",
                            "unknown_reference",
                            "does not reference a logged interaction-evidence artifact",
                        )
            if len(checked_dependencies) != len(set(checked_dependencies)):
                _add(
                    issues,
                    f"{meta_path}.new_evidence_dependency_ids",
                    "duplicate_value",
                    "must not repeat evidence identifiers",
                )
            if set(checked_dependencies) != required_dependency_ids:
                _add(
                    issues,
                    f"{meta_path}.new_evidence_dependency_ids",
                    "evidence_dependency_conflict",
                    "must exactly list evidence supporting new_evidence_requires_inclusion statuses",
                )
        if judgment_scope == "revised_manuscript" and not any(
            evidence_kinds.get(evidence_id) == "revised_manuscript"
            for evidence_id in checked_dependencies
        ):
            _add(
                issues,
                f"{meta_path}.judgment_scope",
                "revised_manuscript_evidence_missing",
                "requires a hashed revised_manuscript evidence dependency",
            )
        _validate_string_array(meta.get("limitations"), f"{meta_path}.limitations", issues)
        _nonempty_string(meta.get("rationale"), f"{meta_path}.rationale", issues)


def validate_bundle(
    bundle: Any,
    *,
    trusted_model_families: Optional[Set[str]] = None,
    trusted_initial_review_sha256: Optional[str] = None,
    trusted_prior_review_sha256: Optional[str] = None,
    trusted_prior_finding_ids: Optional[Set[str]] = None,
) -> List[ValidationIssue]:
    """Return all deterministic structural and consistency failures."""

    issues: List[ValidationIssue] = []
    required = {
        "bundle_version",
        "mode",
        "assurance",
        "created_at",
        "input_scope",
        "privacy",
        "initial_report",
        "artifact_manifest",
        "reviewers",
        "findings",
        "critical_verifications",
        "chair",
    }
    root = _object(
        bundle,
        "$",
        issues,
        required=required,
        allowed=required | {"interaction_log", "focus_areas", "re_review_context"},
    )
    if root is None:
        return sorted(issues)

    version = _nonempty_string(root.get("bundle_version"), "$.bundle_version", issues)
    if version is not None and version != SUPPORTED_VERSION:
        _add(issues, "$.bundle_version", "version", f"must equal supported version {SUPPORTED_VERSION}")
    mode = _enum(root.get("mode"), "$.mode", issues, MODES)
    assurance = _enum(root.get("assurance"), "$.assurance", issues, ASSURANCE_LEVELS)
    _date_time(root.get("created_at"), "$.created_at", issues)

    material_scope, complete_scope = _validate_input_scope(
        root.get("input_scope"), issues
    )
    privacy_mode = _validate_privacy_record(root.get("privacy"), issues)
    _validate_initial_report(root.get("initial_report"), issues)
    page_counts = _validate_manifest(root.get("artifact_manifest"), issues)
    reviewer_ids = _validate_reviewers(
        root.get("reviewers"), assurance, trusted_model_families, issues
    )
    reviewer_roles = {
        reviewer.get("id"): reviewer.get("role")
        for reviewer in root.get("reviewers", [])
        if isinstance(reviewer, dict)
        and isinstance(reviewer.get("id"), str)
        and isinstance(reviewer.get("role"), str)
    }
    reviewer_sealed = {
        reviewer.get("id"): reviewer.get("sealed")
        for reviewer in root.get("reviewers", [])
        if isinstance(reviewer, dict)
        and isinstance(reviewer.get("id"), str)
        and isinstance(reviewer.get("sealed"), bool)
    }
    _validate_mode_roles(mode, root.get("reviewers"), issues)
    _validate_focus_scope(mode, root, issues)
    findings = _validate_findings(
        root.get("findings"), reviewer_ids, page_counts, material_scope, complete_scope, issues
    )
    _validate_finding_verification_privacy(
        privacy_mode, root.get("privacy"), findings, issues
    )
    _validate_focused_findings(mode, root, findings, issues)
    _validate_re_review_context(
        mode,
        root,
        findings,
        trusted_prior_review_sha256,
        trusted_prior_finding_ids,
        issues,
    )
    _validate_critical_verifications(
        root.get("critical_verifications"),
        reviewer_ids,
        reviewer_roles,
        reviewer_sealed,
        findings,
        issues,
    )
    _validate_chair(root.get("chair"), reviewer_ids, findings, issues)
    _validate_input_scope_decision(material_scope, complete_scope, root, issues)
    if "interaction_log" in root:
        if mode != "interactive":
            _add(
                issues,
                "$.mode",
                "interaction_mode_conflict",
                "a bundle with interaction_log must use interactive mode",
            )
        _validate_interaction_log(
            root.get("interaction_log"),
            root,
            findings,
            privacy_mode,
            trusted_initial_review_sha256,
            trusted_prior_review_sha256,
            trusted_prior_finding_ids,
            issues,
        )
    elif mode == "interactive":
        _add(
            issues,
            "$.interaction_log",
            "required",
            "is required when mode is interactive",
        )
    return sorted(issues)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the structure and internal consistency of an AI/cybersecurity "
            "paper-review JSON bundle. This does not validate semantic truth."
        )
    )
    parser.add_argument("bundle", type=Path, help="review-bundle JSON file")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="emit a machine-readable validation result",
    )
    output_group.add_argument(
        "--print-initial-review-sha256",
        action="store_true",
        help=(
            "validate a pre-interaction bundle and print its canonical digest for "
            "detached retention"
        ),
    )
    parser.add_argument(
        "--model-family-registry",
        type=Path,
        help=(
            "detached curator-controlled registry required for cross_model_advisory"
        ),
    )
    parser.add_argument(
        "--trusted-initial-review-sha256",
        help="detached digest retained before the interactive author exchange",
    )
    parser.add_argument(
        "--trusted-prior-review-sha256",
        help="detached digest retained with the review being re-reviewed",
    )
    parser.add_argument(
        "--trusted-prior-review-bundle",
        type=Path,
        help="retained prior review bundle used to derive the authoritative prior finding IDs",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    try:
        bundle = load_bundle(args.bundle)
        trusted_model_families = (
            load_model_family_registry(args.model_family_registry)
            if args.model_family_registry is not None
            else None
        )
        trusted_prior_finding_ids: Optional[Set[str]] = None
        if args.trusted_prior_review_bundle is not None:
            prior_bundle = load_bundle(args.trusted_prior_review_bundle)
            if not isinstance(prior_bundle, dict) or not isinstance(
                prior_bundle.get("findings"), list
            ):
                raise ValueError("trusted prior review bundle must contain a findings array")
            trusted_prior_finding_ids = {
                finding["id"]
                for finding in prior_bundle["findings"]
                if isinstance(finding, dict) and isinstance(finding.get("id"), str)
            }
            if len(trusted_prior_finding_ids) != len(prior_bundle["findings"]):
                raise ValueError(
                    "every trusted prior-review finding must have a unique string id"
                )
            loaded_prior_digest = canonical_json_sha256(prior_bundle)
            if (
                args.trusted_prior_review_sha256 is not None
                and loaded_prior_digest != args.trusted_prior_review_sha256
            ):
                raise ValueError(
                    "trusted prior-review bundle does not match the detached prior-review digest"
                )
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey, ValueError) as exc:
        if args.json_output:
            print(json.dumps({"valid": False, "errors": [{"path": "$", "code": "input", "message": str(exc)}]}, indent=2))
        else:
            print(f"INVALID: {args.bundle}", file=sys.stderr)
            print(f"[input] $: {exc}", file=sys.stderr)
        return 2

    if args.print_initial_review_sha256 and (
        not isinstance(bundle, dict)
        or bundle.get("mode") == "interactive"
        or "interaction_log" in bundle
    ):
        issues = [
            ValidationIssue(
                path="$.mode",
                code="digest_generation_stage",
                message="detached digest must be generated before interactive mode begins",
            )
        ]
    else:
        issues = validate_bundle(
            bundle,
            trusted_model_families=trusted_model_families,
            trusted_initial_review_sha256=args.trusted_initial_review_sha256,
            trusted_prior_review_sha256=args.trusted_prior_review_sha256,
            trusted_prior_finding_ids=trusted_prior_finding_ids,
        )
    if args.json_output:
        print(
            json.dumps(
                {
                    "valid": not issues,
                    "errors": [asdict(issue) for issue in issues],
                    "assurance_note": (
                        "Validation establishes structure and consistency only; "
                        "it does not establish scientific truth or review quality."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
    elif issues:
        print(f"INVALID: {args.bundle} ({len(issues)} error(s))", file=sys.stderr)
        for issue in issues:
            print(f"[{issue.code}] {issue.path}: {issue.message}", file=sys.stderr)
    elif args.print_initial_review_sha256:
        print(canonical_initial_review_sha256(bundle))
    else:
        print(f"VALID: {args.bundle}")
        print(
            "NOTE: validation proves structural and cross-reference consistency only; "
            "it does not prove semantic truth, completeness, independence, or fairness."
        )
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
