#!/usr/bin/env python3
"""Validate mock-panel schemas, evidence links, provenance, freshness, and run completeness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from aggregate_panel import aggregate_reviews
from build_artifact_manifest import FULL_PANEL_FILES, validate_calibration_semantics
from protocol_digest import protocol_bundle_sha256
from schema_contract import validate_instance


ALLOWED_RATINGS = {"excellent", "very_good", "good", "fair", "poor", "unrated"}
RATING_ORDINAL = {"poor": 1, "fair": 2, "good": 3, "very_good": 4, "excellent": 5}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_SEVERITY = {"blocker", "major", "moderate", "minor"}
ALLOWED_STANCE = {"strength", "weakness", "question"}
ALLOWED_EPISTEMIC = {
    "verified",
    "proposal_grounded",
    "literature_grounded",
    "policy_grounded",
    "inference",
    "open_question",
}
ALLOWED_ASSURANCE = {
    "provisional_advisory",
    "multi_family_advisory",
    "human_calibrated_advisory",
}
REQUIRED_DIMENSIONS = {
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
}
REQUIRED_REVIEWER_PROFILES = {"general_cs", "adjacent_cise", "domain_methods"}
PROFILE_EXPECTED_FAMILIARITY = {
    "general_cs": "non_specialist",
    "adjacent_cise": "adjacent",
    "domain_methods": "specialist",
}
DIMENSION_EXPECTED_GROUPS = {
    "importance_gap": {"intellectual_merit"},
    "novelty_transformative": {"intellectual_merit", "external_novelty"},
    "contribution_intellectual_merit": {"intellectual_merit"},
    "approach_evaluation": {"intellectual_merit", "technical_integrity"},
    "feasibility_team_resources": {"intellectual_merit", "technical_integrity"},
    "broader_impacts": {"broader_impacts"},
    "solicitation_fit": {"intellectual_merit", "additional_criterion"},
    "presentation_organization": {"presentation"},
    "general_cs_accessibility": {"presentation"},
    "writing_precision_professionalism": {"presentation"},
    "technical_precision_integrity": {"technical_integrity"},
}
DIMENSION_EVIDENCE_RULES = {
    "general_cs_accessibility": (
        {"general_cs", "all_panelists"},
        {"comprehension", "navigation", "contribution_clarity"},
    ),
    "writing_precision_professionalism": (
        {"general_cs", "adjacent_cise", "all_panelists"},
        {
            "comprehension",
            "navigation",
            "contribution_clarity",
            "reviewer_confidence",
            "presentation",
        },
    ),
    "technical_precision_integrity": (
        {"domain_or_methods_specialist", "all_panelists"},
        {"scientific_validity", "reviewer_confidence", "feasibility"},
    ),
}
ALLOWED_LEDGER_EVENTS = {
    "created",
    "corroborated",
    "disputed",
    "resolved",
    "partially_resolved",
    "unresolved",
    "superseded",
    "reopened",
    "regressed",
    "not_comparable",
    "rating_changed",
    "chair_claim_verified",
}
STANDARD_TRANSITIONS = {
    "created": {("absent", "open")},
    "corroborated": {("open", "corroborated"), ("corroborated", "corroborated")},
    "disputed": {("open", "under_adjudication"), ("corroborated", "under_adjudication")},
    "resolved": {
        ("open", "resolved"),
        ("corroborated", "resolved"),
        ("under_adjudication", "resolved"),
        ("partially_resolved", "resolved"),
        ("unresolved", "resolved"),
    },
    "partially_resolved": {
        ("open", "partially_resolved"),
        ("corroborated", "partially_resolved"),
        ("under_adjudication", "partially_resolved"),
        ("unresolved", "partially_resolved"),
    },
    "unresolved": {
        ("open", "unresolved"),
        ("corroborated", "unresolved"),
        ("under_adjudication", "unresolved"),
        ("partially_resolved", "unresolved"),
    },
    "superseded": {
        ("open", "superseded"),
        ("corroborated", "superseded"),
        ("under_adjudication", "superseded"),
        ("resolved", "superseded"),
        ("partially_resolved", "superseded"),
        ("unresolved", "superseded"),
    },
    "reopened": {
        ("resolved", "open"),
        ("partially_resolved", "open"),
        ("unresolved", "open"),
        ("superseded", "open"),
        ("not_comparable", "open"),
    },
    "regressed": {("resolved", "open"), ("partially_resolved", "open")},
    "not_comparable": {
        ("open", "not_comparable"),
        ("corroborated", "not_comparable"),
        ("under_adjudication", "not_comparable"),
        ("resolved", "not_comparable"),
        ("partially_resolved", "not_comparable"),
        ("unresolved", "not_comparable"),
    },
}


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


def atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def add_error(errors: list[str], label: str, message: str) -> None:
    errors.append(f"{label}: {message}")


def apply_schema(
    value: dict[str, Any], schema: dict[str, Any], label: str, errors: list[str]
) -> None:
    for message in validate_instance(value, schema, path=label):
        errors.append(message)


def load_contract_schemas() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    assets = Path(__file__).resolve().parents[1] / "assets"
    return (
        load_json(assets / "individual-review.schema.json"),
        load_json(assets / "panel-summary.schema.json"),
        load_json(assets / "human-calibration-record.schema.json"),
    )


def validate_manifest_files(
    manifest: dict[str, Any], errors: list[str]
) -> tuple[dict[str, str], set[str], set[str]]:
    hashes: dict[str, str] = {}
    proposal_hashes: set[str] = set()
    authority_paths: set[str] = set()
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        add_error(errors, "manifest.files", "must be a non-empty array")
        return hashes, proposal_hashes, authority_paths
    for index, record in enumerate(records):
        label = f"manifest.files[{index}]"
        if not isinstance(record, dict):
            add_error(errors, label, "must be an object")
            continue
        path = Path(str(record.get("absolute_path", "")))
        expected = str(record.get("sha256", ""))
        display = str(record.get("path", path))
        role = str(record.get("role", ""))
        if display in hashes:
            add_error(errors, label, f"duplicate display path {display!r}")
        if not path.is_file():
            add_error(errors, label, f"pinned file missing: {path}")
        else:
            actual = sha256_file(path)
            if actual != expected:
                add_error(
                    errors,
                    label,
                    f"stale hash for {display}: expected {expected}, found {actual}",
                )
        hashes[display] = expected
        if role == "proposal":
            proposal_hashes.add(expected)
        elif role == "authority":
            authority_paths.add(str(path.resolve()))
    if not proposal_hashes:
        add_error(errors, "manifest.files", "at least one proposal input is required")
    return hashes, proposal_hashes, authority_paths


def validate_manifest_metadata(
    manifest: dict[str, Any], mode: str, errors: list[str], warnings: list[str]
) -> str:
    if manifest.get("schema_version") != "1.0":
        add_error(errors, "manifest", "schema_version must be '1.0'")
    proposal_id = str(manifest.get("proposal_id", "")).strip()
    if not proposal_id:
        add_error(errors, "manifest", "proposal_id is required")
    authorization = manifest.get("processing_authorization")
    if not isinstance(authorization, dict):
        add_error(errors, "manifest", "processing_authorization must be an object")
        authorization = {}
    classification = authorization.get("classification")
    if classification == "official-nsf-review-material":
        add_error(errors, "manifest", "official NSF review material is not permitted")
    if classification not in {
        "proposer-owned",
        "organization-authorized",
        "public",
        "third-party-confidential",
    }:
        add_error(errors, "manifest", "invalid or missing permitted classification")
    if not str(authorization.get("processing_boundary", "")).strip():
        add_error(errors, "manifest", "processing_boundary is required")

    policy = manifest.get("policy")
    if not isinstance(policy, dict):
        add_error(errors, "manifest", "policy must be an object")
        policy = {}
    policy_status = policy.get("status")
    if mode in {"review-gate", "full-panel"} and policy_status != "authority_pinned":
        add_error(
            errors,
            "manifest",
            "review-gate/full-panel requires a recent hash-pinned authority snapshot",
        )
    elif policy_status != "authority_pinned":
        warnings.append(f"manifest: policy snapshot status is {policy_status or 'missing'}")
    return proposal_id


def validate_finding_semantics(finding: dict[str, Any], label: str, errors: list[str]) -> None:
    if finding.get("severity") not in ALLOWED_SEVERITY:
        add_error(errors, label, f"invalid severity {finding.get('severity')!r}")
    if finding.get("stance") not in ALLOWED_STANCE:
        add_error(errors, label, f"invalid stance {finding.get('stance')!r}")
    if finding.get("epistemic_status") not in ALLOWED_EPISTEMIC:
        add_error(errors, label, f"invalid epistemic_status {finding.get('epistemic_status')!r}")
    stance = finding.get("stance")
    revision_type = finding.get("revision_type")
    if stance == "strength" and revision_type != "preserve_or_reinforce":
        add_error(errors, label, "a strength must use revision_type 'preserve_or_reinforce'")
    if stance == "weakness" and revision_type == "preserve_or_reinforce":
        add_error(errors, label, "a weakness must identify a corrective revision_type")


def validate_finding_references(
    values: Any,
    finding_by_id: dict[str, dict[str, Any]],
    label: str,
    expected_stance: str,
    expected_group: str,
    errors: list[str],
    *,
    require_nonempty: bool,
) -> None:
    if not isinstance(values, list) or (require_nonempty and not values):
        requirement = "a non-empty array" if require_nonempty else "an array"
        add_error(errors, label, f"must be {requirement}")
        return
    for finding_id in values:
        finding = finding_by_id.get(str(finding_id))
        if finding is None:
            add_error(errors, label, f"references unknown {finding_id!r}")
            continue
        if finding.get("stance") != expected_stance:
            add_error(errors, label, f"{finding_id!r} has wrong stance")
        if finding.get("criterion_group") != expected_group:
            add_error(errors, label, f"{finding_id!r} has wrong criterion_group")


def validate_coverage_section(
    section: Any,
    group: str,
    label: str,
    findings: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    accepted_audiences: set[str],
    accepted_impacts: set[str],
) -> None:
    """Validate a section that may report only strengths or only weaknesses."""

    if not isinstance(section, dict):
        return
    strength_ids = section.get("strength_finding_ids")
    weakness_ids = section.get("weakness_finding_ids")
    validate_finding_references(
        strength_ids,
        findings,
        f"{label}.strength_finding_ids",
        "strength",
        group,
        errors,
        require_nonempty=False,
    )
    validate_finding_references(
        weakness_ids,
        findings,
        f"{label}.weakness_finding_ids",
        "weakness",
        group,
        errors,
        require_nonempty=False,
    )
    if isinstance(strength_ids, list) and isinstance(weakness_ids, list):
        if not strength_ids and not weakness_ids:
            add_error(errors, label, "must cite at least one strength or weakness finding")
        referenced = [
            findings[str(finding_id)]
            for finding_id in [*strength_ids, *weakness_ids]
            if str(finding_id) in findings
        ]
        if referenced and not any(
            accepted_audiences.intersection(finding.get("audiences_affected", []))
            and accepted_impacts.intersection(finding.get("impact_types", []))
            for finding in referenced
        ):
            add_error(
                errors,
                label,
                "does not cite a finding with the required audience and impact coverage",
            )
        assessment = section.get("assessment")
        stances = {str(finding.get("stance", "")) for finding in referenced}
        if assessment == "strong" and "strength" not in stances:
            add_error(errors, label, "strong assessment requires a linked strength finding")
        if assessment == "weak" and "weakness" not in stances:
            add_error(errors, label, "weak assessment requires a linked weakness finding")


def additional_criterion_keys(review: dict[str, Any]) -> set[tuple[str, str]]:
    value = review.get("additional_criteria")
    if not isinstance(value, list):
        return set()
    return {
        (str(entry.get("criterion", "")).strip(), str(entry.get("source", "")).strip())
        for entry in value
        if isinstance(entry, dict)
        and str(entry.get("criterion", "")).strip()
        and str(entry.get("source", "")).strip()
    }


def validate_review(
    review: dict[str, Any],
    label: str,
    schema: dict[str, Any],
    expected_hashes: dict[str, str],
    proposal_id: str,
    errors: list[str],
    warnings: list[str],
) -> dict[str, dict[str, Any]]:
    apply_schema(review, schema, label, errors)
    if review.get("proposal_id") != proposal_id:
        add_error(errors, label, "proposal_id does not match the packet manifest")

    reviewer_profile = review.get("reviewer_profile")
    if isinstance(reviewer_profile, dict):
        profile_id = str(reviewer_profile.get("profile_id", ""))
        expected_familiarity = PROFILE_EXPECTED_FAMILIARITY.get(profile_id)
        if (
            expected_familiarity is not None
            and reviewer_profile.get("domain_familiarity") != expected_familiarity
        ):
            add_error(
                errors,
                label,
                f"reviewer profile {profile_id!r} requires domain_familiarity "
                f"{expected_familiarity!r}",
            )

    reviewer_route = review.get("reviewer_route")
    if isinstance(reviewer_route, dict) and reviewer_route.get("provenance_source") in {
        "self_reported",
        "unavailable",
    }:
        warnings.append(
            f"{label}: reviewer route provenance is not independently recorded; "
            "multi-family assurance is unavailable"
        )

    conflict = review.get("conflict_check")
    if isinstance(conflict, dict):
        status = conflict.get("status")
        if status == "blocked":
            add_error(errors, label, "reviewer conflict status is blocked")
        elif status in {"potential", "not_assessed"}:
            warnings.append(f"{label}: conflict status is {status}")

    rating = review.get("rating")
    if isinstance(rating, dict):
        value = rating.get("value")
        adjacent = rating.get("adjacent_split")
        if adjacent is not None:
            if value not in RATING_ORDINAL or adjacent not in RATING_ORDINAL:
                add_error(errors, label, "adjacent_split is invalid for an unrated review")
            elif abs(RATING_ORDINAL[value] - RATING_ORDINAL[adjacent]) != 1:
                add_error(errors, label, "adjacent_split must be exactly one rating band away")

    reviewed_hashes = review.get("reviewed_input_hashes")
    if reviewed_hashes != expected_hashes:
        add_error(errors, label, "reviewed_input_hashes must exactly match the packet manifest")

    findings_value = review.get("findings")
    findings = findings_value if isinstance(findings_value, list) else []
    finding_by_id: dict[str, dict[str, Any]] = {}
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        finding_label = f"{label}.findings[{index}]"
        validate_finding_semantics(finding, finding_label, errors)
        finding_id = finding.get("id")
        if isinstance(finding_id, str):
            if finding_id in finding_by_id:
                add_error(errors, finding_label, f"duplicate finding ID {finding_id!r}")
            finding_by_id[finding_id] = finding

    for section_name, group in (
        ("intellectual_merit", "intellectual_merit"),
        ("broader_impacts", "broader_impacts"),
    ):
        section = review.get(section_name)
        if not isinstance(section, dict):
            continue
        validate_finding_references(
            section.get("strength_finding_ids"),
            finding_by_id,
            f"{label}.{section_name}.strength_finding_ids",
            "strength",
            group,
            errors,
            require_nonempty=True,
        )
        validate_finding_references(
            section.get("weakness_finding_ids"),
            finding_by_id,
            f"{label}.{section_name}.weakness_finding_ids",
            "weakness",
            group,
            errors,
            require_nonempty=True,
        )

    validate_coverage_section(
        review.get("writing_and_accessibility"),
        "presentation",
        f"{label}.writing_and_accessibility",
        finding_by_id,
        errors,
        accepted_audiences={"general_cs", "adjacent_cise", "all_panelists"},
        accepted_impacts={
            "comprehension",
            "navigation",
            "contribution_clarity",
            "reviewer_confidence",
            "presentation",
        },
    )
    validate_coverage_section(
        review.get("technical_precision_integrity"),
        "technical_integrity",
        f"{label}.technical_precision_integrity",
        finding_by_id,
        errors,
        accepted_audiences={"domain_or_methods_specialist", "all_panelists"},
        accepted_impacts={"scientific_validity", "reviewer_confidence", "feasibility"},
    )

    additional = review.get("additional_criteria")
    if isinstance(additional, list):
        keys = [
            (str(item.get("criterion", "")).strip(), str(item.get("source", "")).strip())
            for item in additional
            if isinstance(item, dict)
        ]
        if len(keys) != len(set(keys)):
            add_error(errors, label, "additional criteria must be unique by criterion and source")
        for index, criterion in enumerate(additional):
            if not isinstance(criterion, dict):
                continue
            for key, stance in (
                ("strength_finding_ids", "strength"),
                ("weakness_finding_ids", "weakness"),
            ):
                validate_finding_references(
                    criterion.get(key),
                    finding_by_id,
                    f"{label}.additional_criteria[{index}].{key}",
                    stance,
                    "additional_criterion",
                    errors,
                    require_nonempty=False,
                )

    dimensions = review.get("dimensions")
    if isinstance(dimensions, dict):
        missing = sorted(REQUIRED_DIMENSIONS - set(dimensions))
        unexpected = sorted(set(dimensions) - REQUIRED_DIMENSIONS)
        if missing:
            add_error(errors, label, f"missing dimensions: {', '.join(missing)}")
        if unexpected:
            add_error(errors, label, f"unexpected dimensions: {', '.join(unexpected)}")
        for name, entry in dimensions.items():
            if not isinstance(entry, dict):
                continue
            finding_ids = entry.get("finding_ids")
            if isinstance(finding_ids, list):
                if not finding_ids:
                    add_error(errors, label, f"dimension {name!r} must cite at least one finding")
                linked_findings: list[dict[str, Any]] = []
                for finding_id in finding_ids:
                    finding = finding_by_id.get(str(finding_id))
                    if finding is None:
                        add_error(errors, label, f"dimension {name!r} references unknown {finding_id!r}")
                        continue
                    expected_groups = DIMENSION_EXPECTED_GROUPS.get(name, set())
                    if finding.get("criterion_group") not in expected_groups:
                        add_error(
                            errors,
                            label,
                            f"dimension {name!r} references {finding_id!r} with wrong criterion_group",
                        )
                    else:
                        linked_findings.append(finding)
                assessment = entry.get("assessment")
                stances = {str(finding.get("stance", "")) for finding in linked_findings}
                if assessment == "strong" and "strength" not in stances:
                    add_error(
                        errors,
                        label,
                        f"dimension {name!r} strong assessment requires a linked strength finding",
                    )
                if assessment == "weak" and "weakness" not in stances:
                    add_error(
                        errors,
                        label,
                        f"dimension {name!r} weak assessment requires a linked weakness finding",
                    )
                audience_rule = DIMENSION_EVIDENCE_RULES.get(name)
                if audience_rule and linked_findings:
                    accepted_audiences, accepted_impacts = audience_rule
                    if not any(
                        accepted_audiences.intersection(
                            finding.get("audiences_affected", [])
                        )
                        and accepted_impacts.intersection(
                            finding.get("impact_types", [])
                        )
                        for finding in linked_findings
                    ):
                        add_error(
                            errors,
                            label,
                            f"dimension {name!r} lacks audience-appropriate evidence",
                        )

    independence = review.get("review_independence")
    if independence in {"same-family", "single-context"}:
        warnings.append(f"{label}: semantic assurance is provisional ({independence})")
    return finding_by_id


def validate_panel_criterion(
    section: Any,
    group: str,
    label: str,
    findings: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    require_nonempty: bool,
) -> None:
    if not isinstance(section, dict):
        return
    validate_finding_references(
        section.get("strength_finding_ids"),
        findings,
        f"{label}.strength_finding_ids",
        "strength",
        group,
        errors,
        require_nonempty=require_nonempty,
    )
    validate_finding_references(
        section.get("weakness_finding_ids"),
        findings,
        f"{label}.weakness_finding_ids",
        "weakness",
        group,
        errors,
        require_nonempty=require_nonempty,
    )


def derive_assurance(
    reviews: list[dict[str, Any]],
    human_calibration_passed: bool,
    chair_route_trusted: bool,
) -> str:
    families = {
        str(review.get("reviewer_family", "")).strip()
        for review in reviews
        if str(review.get("reviewer_family", "")).strip()
    }
    independence = {str(review.get("review_independence", "")) for review in reviews}
    route_sources = [
        str(review.get("reviewer_route", {}).get("provenance_source", ""))
        for review in reviews
        if isinstance(review.get("reviewer_route"), dict)
    ]
    trusted_route_provenance = (
        len(route_sources) == len(reviews)
        and all(
            source in {"runtime_metadata", "human_attestation"}
            for source in route_sources
        )
    )
    eligible_route_topology = (
        trusted_route_provenance
        and independence <= {"cross-family", "human"}
    )
    if human_calibration_passed and chair_route_trusted and eligible_route_topology:
        return "human_calibrated_advisory"
    if (
        len(families) >= 2
        and eligible_route_topology
    ):
        return "multi_family_advisory"
    return "provisional_advisory"


def validate_panel(
    panel: dict[str, Any],
    label: str,
    schema: dict[str, Any],
    proposal_id: str,
    reviewer_ids: set[str],
    reviewer_route_ids: set[str],
    reviewer_model_families: dict[str, set[str]],
    review_hashes: dict[str, str],
    findings: dict[str, dict[str, Any]],
    initial_ratings: dict[str, str],
    expected_additional_criteria: set[tuple[str, str]],
    expected_disagreement_keys: set[tuple[str, str]],
    derived_assurance: str,
    require_post_check: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    apply_schema(panel, schema, label, errors)
    if panel.get("proposal_id") != proposal_id:
        add_error(errors, label, "proposal_id does not match the packet manifest")
    listed = panel.get("reviewer_ids")
    if not isinstance(listed, list) or set(str(value) for value in listed) != reviewer_ids:
        add_error(errors, label, "reviewer_ids must exactly match individual reviews")
    if panel.get("source_review_hashes") != review_hashes:
        add_error(errors, label, "source_review_hashes must exactly match frozen reviews")

    chair = panel.get("chair")
    if isinstance(chair, dict):
        chair_route_id = str(chair.get("route_id", "")).strip()
        if chair_route_id and chair_route_id in reviewer_route_ids:
            add_error(errors, label, "chair route_id must be distinct from reviewer routes")
        chair_model = str(chair.get("model", "")).strip()
        chair_family = str(chair.get("family", "")).strip()
        if (
            chair_model in reviewer_model_families
            and chair_family
            and chair_family not in reviewer_model_families[chair_model]
        ):
            add_error(errors, label, "chair model-to-family mapping contradicts a reviewer")
        if chair.get("provenance_source") in {"self_reported", "unavailable"}:
            warnings.append(
                f"{label}: chair route provenance is not independently recorded"
            )

    validate_panel_criterion(
        panel.get("intellectual_merit"),
        "intellectual_merit",
        f"{label}.intellectual_merit",
        findings,
        errors,
        require_nonempty=True,
    )
    validate_coverage_section(
        panel.get("writing_and_accessibility"),
        "presentation",
        f"{label}.writing_and_accessibility",
        findings,
        errors,
        accepted_audiences={"general_cs", "adjacent_cise", "all_panelists"},
        accepted_impacts={
            "comprehension",
            "navigation",
            "contribution_clarity",
            "reviewer_confidence",
            "presentation",
        },
    )
    validate_coverage_section(
        panel.get("technical_precision_integrity"),
        "technical_integrity",
        f"{label}.technical_precision_integrity",
        findings,
        errors,
        accepted_audiences={"domain_or_methods_specialist", "all_panelists"},
        accepted_impacts={"scientific_validity", "reviewer_confidence", "feasibility"},
    )
    validate_panel_criterion(
        panel.get("broader_impacts"),
        "broader_impacts",
        f"{label}.broader_impacts",
        findings,
        errors,
        require_nonempty=True,
    )
    additional = panel.get("additional_criteria")
    if isinstance(additional, list):
        panel_keys = [
            (str(item.get("criterion", "")).strip(), str(item.get("source", "")).strip())
            for item in additional
            if isinstance(item, dict)
        ]
        if len(panel_keys) != len(set(panel_keys)):
            add_error(errors, label, "additional criteria must be unique by criterion and source")
        if set(panel_keys) != expected_additional_criteria:
            missing = sorted(expected_additional_criteria - set(panel_keys))
            unexpected = sorted(set(panel_keys) - expected_additional_criteria)
            details: list[str] = []
            if missing:
                details.append(f"missing {missing!r}")
            if unexpected:
                details.append(f"unexpected {unexpected!r}")
            add_error(
                errors,
                label,
                "panel additional criteria do not match sealed reviews: " + "; ".join(details),
            )
        for index, criterion in enumerate(additional):
            if not isinstance(criterion, dict):
                continue
            for key, stance in (
                ("strength_finding_ids", "strength"),
                ("weakness_finding_ids", "weakness"),
            ):
                validate_finding_references(
                    criterion.get(key),
                    findings,
                    f"{label}.additional_criteria[{index}].{key}",
                    stance,
                    "additional_criterion",
                    errors,
                    require_nonempty=False,
                )

    disagreements_value = panel.get("disagreements")
    disagreements = disagreements_value if isinstance(disagreements_value, list) else []
    panel_disagreement_keys = [
        (str(item.get("topic_key", "")), str(item.get("kind", "")))
        for item in disagreements
        if isinstance(item, dict)
    ]
    if len(panel_disagreement_keys) != len(set(panel_disagreement_keys)):
        add_error(errors, label, "panel disagreement topic_key/kind pairs must be unique")
    missing_disagreements = sorted(
        expected_disagreement_keys - set(panel_disagreement_keys)
    )
    if missing_disagreements:
        add_error(
            errors,
            label,
            "panel disagreements omit mechanically flagged topics: "
            + ", ".join(f"{topic}/{kind}" for topic, kind in missing_disagreements),
        )

    rating_changes_value = panel.get("rating_changes")
    rating_changes = rating_changes_value if isinstance(rating_changes_value, list) else []
    rating_change_reviewers = [
        str(change.get("reviewer_id", ""))
        for change in rating_changes
        if isinstance(change, dict)
    ]
    if len(rating_change_reviewers) != len(set(rating_change_reviewers)):
        add_error(errors, label, "rating_changes may contain each reviewer only once")
    for index, change in enumerate(rating_changes):
        if not isinstance(change, dict):
            continue
        change_label = f"{label}.rating_changes[{index}]"
        reviewer_id = str(change.get("reviewer_id", ""))
        if initial_ratings.get(reviewer_id) != change.get("initial"):
            add_error(errors, change_label, "initial rating does not match frozen review")
        if change.get("initial") == change.get("revised"):
            add_error(errors, change_label, "revised rating must differ from initial rating")

    claims_value = panel.get("chair_introduced_claims")
    chair_claims = claims_value if isinstance(claims_value, list) else []
    claim_ids = [str(claim.get("id", "")) for claim in chair_claims if isinstance(claim, dict)]
    if len(claim_ids) != len(set(claim_ids)):
        add_error(errors, label, "chair-introduced claim IDs must be unique")

    assurance = panel.get("assurance_label")
    if assurance not in ALLOWED_ASSURANCE:
        add_error(errors, label, "invalid assurance_label")
    elif assurance != derived_assurance:
        add_error(
            errors,
            label,
            f"assurance_label is self-inconsistent: expected {derived_assurance!r}",
        )

    post_check = panel.get("post_chair_verification")
    if isinstance(post_check, dict):
        if post_check.get("status") == "not_run":
            if require_post_check:
                add_error(errors, label, "full-panel post-chair verification was not run")
            else:
                warnings.append(f"{label}: post-chair verification was not run")
        elif post_check.get("status") == "failed":
            add_error(errors, label, "post-chair verification failed")

    panel_text = str(panel).lower()
    if any(
        phrase in panel_text
        for phrase in ("funding probability", "chance of funding", "likelihood of funding")
    ):
        warnings.append(f"{label}: remove funding-probability language")
    return rating_changes, chair_claims


def validate_artifact_manifest(
    run_manifest: dict[str, Any],
    run_manifest_path: Path,
    packet_path: Path,
    proposal_id: str,
    authority_paths: set[str],
    review_records: list[tuple[Path, dict[str, Any]]],
    review_paths: list[Path],
    review_hashes: dict[str, str],
    panel_path: Path,
    ledger_path: Path,
    calibration_schema: dict[str, Any],
    expected_model_families: set[str],
    expected_model_ids: set[str],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], bool]:
    label = run_manifest_path.name
    if run_manifest.get("schema_version") != "1.0":
        add_error(errors, label, "schema_version must be '1.0'")
    if run_manifest.get("mode") != "full-panel":
        add_error(errors, label, "mode must be full-panel")
    if run_manifest.get("proposal_id") != proposal_id:
        add_error(errors, label, "proposal_id does not match packet")
    packet_record = run_manifest.get("packet_manifest")
    if not isinstance(packet_record, dict):
        add_error(errors, label, "packet_manifest record is required")
    else:
        if str(Path(str(packet_record.get("absolute_path", ""))).resolve()) != str(packet_path):
            add_error(errors, label, "packet manifest path does not match")
        if packet_record.get("sha256") != sha256_file(packet_path):
            add_error(errors, label, "packet manifest hash is stale")

    artifacts_value = run_manifest.get("artifacts")
    artifacts = artifacts_value if isinstance(artifacts_value, list) else []
    by_role: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(artifacts):
        record_label = f"{label}.artifacts[{index}]"
        if not isinstance(record, dict):
            add_error(errors, record_label, "must be an object")
            continue
        role = str(record.get("role", ""))
        if not role:
            add_error(errors, record_label, "role is required")
            continue
        if role in by_role:
            add_error(errors, record_label, f"duplicate role {role!r}")
        by_role[role] = record
        path = Path(str(record.get("absolute_path", ""))).resolve()
        if not path.is_file():
            add_error(errors, record_label, f"artifact is missing: {path}")
            continue
        if record.get("sha256") != sha256_file(path):
            add_error(errors, record_label, f"artifact hash is stale: {path}")
        if path.stat().st_size == 0:
            add_error(errors, record_label, f"artifact is empty: {path}")

    required_roles = set(FULL_PANEL_FILES)
    missing = sorted(required_roles - set(by_role))
    if missing:
        add_error(errors, label, f"missing full-panel artifact roles: {', '.join(missing)}")

    expected_review_roles = ("review_r1_json", "review_r2_json", "review_r3_json")
    manifested_reviews = {
        str(Path(str(by_role[role].get("absolute_path", ""))).resolve())
        for role in expected_review_roles
        if role in by_role
    }
    if manifested_reviews != {str(path) for path in review_paths}:
        add_error(errors, label, "review JSON paths do not match artifact manifest")
    for role, expected_path in (
        ("panel_summary_json", panel_path),
        ("issue_ledger", ledger_path),
    ):
        if role in by_role:
            actual_path = Path(str(by_role[role].get("absolute_path", ""))).resolve()
            if actual_path != expected_path:
                add_error(errors, label, f"{role} path does not match command input")
    if "authority_snapshot" in by_role:
        authority_path = str(
            Path(str(by_role["authority_snapshot"].get("absolute_path", ""))).resolve()
        )
        if authority_path not in authority_paths:
            add_error(errors, label, "authority snapshot was not pinned in the packet manifest")

    if "pre_deliberation_validation" in by_role:
        gate_path = Path(
            str(by_role["pre_deliberation_validation"].get("absolute_path", ""))
        ).resolve()
        try:
            gate = load_json(gate_path)
        except ValueError as exc:
            add_error(errors, label, str(exc))
        else:
            if (
                gate.get("mode") != "review-gate"
                or gate.get("verdict") not in {"PASS", "WARN"}
                or gate.get("errors")
            ):
                add_error(errors, label, "pre-deliberation gate did not pass structurally")
            if gate.get("proposal_id") != proposal_id:
                add_error(errors, label, "pre-deliberation gate proposal_id does not match")
            if gate.get("packet_manifest_hash") != sha256_file(packet_path):
                add_error(errors, label, "pre-deliberation gate packet hash does not match")
            if gate.get("validated_review_hashes") != review_hashes:
                add_error(errors, label, "pre-deliberation gate review hashes do not match")
            if gate.get("review_count", 0) < 3:
                add_error(errors, label, "pre-deliberation gate covered fewer than three reviews")

    if "panel_aggregate" in by_role:
        aggregate_path = Path(
            str(by_role["panel_aggregate"].get("absolute_path", ""))
        ).resolve()
        try:
            aggregate = load_json(aggregate_path)
        except ValueError as exc:
            add_error(errors, label, str(exc))
        else:
            generated_at = str(aggregate.get("generated_at", ""))
            try:
                aggregate_timestamp = datetime.fromisoformat(
                    generated_at.replace("Z", "+00:00")
                )
                if aggregate_timestamp.tzinfo is None:
                    raise ValueError
            except ValueError:
                add_error(errors, label, "panel aggregate generated_at must be timezone-aware ISO 8601")
            try:
                expected_aggregate = aggregate_reviews(
                    review_records, generated_at=generated_at
                )
            except (KeyError, TypeError, ValueError) as exc:
                add_error(errors, label, f"cannot rederive panel aggregate: {exc}")
            else:
                if aggregate != expected_aggregate:
                    add_error(
                        errors,
                        label,
                        "panel aggregate does not exactly match the frozen reviews",
                    )

    human_calibration_passed = False
    if "human_calibration_record" in by_role:
        calibration_error_count = len(errors)
        calibration_path = Path(
            str(by_role["human_calibration_record"].get("absolute_path", ""))
        ).resolve()
        try:
            calibration = load_json(calibration_path)
        except ValueError as exc:
            add_error(errors, label, str(exc))
        else:
            apply_schema(
                calibration,
                calibration_schema,
                calibration_path.name,
                errors,
            )
            try:
                validate_calibration_semantics(calibration)
            except ValueError as exc:
                add_error(errors, label, str(exc))
            skill_profile = calibration.get("skill_profile")
            if isinstance(skill_profile, dict):
                current_protocol_hash = protocol_bundle_sha256(
                    Path(__file__).resolve().parents[1]
                )
                if (
                    skill_profile.get("protocol_bundle_sha256")
                    != current_protocol_hash
                ):
                    add_error(errors, label, "human calibration protocol bundle hash is stale")
                calibrated_families = {
                    str(value)
                    for value in skill_profile.get("model_families", [])
                    if str(value).strip()
                }
                missing_families = sorted(expected_model_families - calibrated_families)
                if missing_families:
                    add_error(
                        errors,
                        label,
                        "human calibration does not cover model families: "
                        + ", ".join(missing_families),
                    )
                calibrated_models = {
                    str(value)
                    for value in skill_profile.get("model_ids", [])
                    if str(value).strip()
                }
                missing_models = sorted(expected_model_ids - calibrated_models)
                if missing_models:
                    add_error(
                        errors,
                        label,
                        "human calibration does not cover model identifiers: "
                        + ", ".join(missing_models),
                    )
            result = calibration.get("result")
            human_calibration_passed = (
                isinstance(result, dict) and result.get("status") == "passed"
                and len(errors) == calibration_error_count
            )
    return by_role, human_calibration_passed


def validate_evidence_objects(evidence: Any, label: str, errors: list[str]) -> None:
    if not isinstance(evidence, list) or not evidence:
        add_error(errors, label, "evidence must be a non-empty array")
        return
    for index, anchor in enumerate(evidence):
        if (
            not isinstance(anchor, dict)
            or not str(anchor.get("source", "")).strip()
            or not str(anchor.get("location", "")).strip()
        ):
            add_error(errors, label, f"evidence[{index}] requires source and location")


def valid_event_transition(event: dict[str, Any]) -> bool:
    kind = event.get("event")
    prior = event.get("prior_state")
    new = event.get("new_state")
    if kind in STANDARD_TRANSITIONS:
        return (prior, new) in STANDARD_TRANSITIONS[kind]
    if kind == "rating_changed":
        return prior in ALLOWED_RATINGS and new in ALLOWED_RATINGS and prior != new
    if kind == "chair_claim_verified":
        return prior == "unverified" and new in {"verified", "qualified", "rejected", "unresolved"}
    return False


def validate_ledger(
    path: Path,
    proposal_hashes: set[str],
    finding_ids: set[str],
    reviewer_ids: set[str],
    chair_claim_ids: set[str],
    errors: list[str],
) -> tuple[int, dict[tuple[str, str], list[dict[str, Any]]]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        add_error(errors, path.name, f"cannot read ledger: {exc}")
        return 0, {}
    if not lines:
        add_error(errors, path.name, "ledger must contain at least one event")
        return 0, {}

    allowed_special_ids = {f"rating:{reviewer_id}" for reviewer_id in reviewer_ids} | chair_claim_ids
    seen_findings: set[str] = set()
    current_state: dict[str, str] = {}
    prior_timestamp: datetime | None = None
    events_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    event_count = 0
    for line_number, line in enumerate(lines, start=1):
        label = f"{path.name}:{line_number}"
        if not line.strip():
            add_error(errors, label, "blank lines are not allowed in JSONL")
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            add_error(errors, label, f"invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            add_error(errors, label, "event must be an object")
            continue
        event_count += 1
        for field in (
            "timestamp",
            "proposal_hash",
            "actor",
            "finding_id",
            "event",
            "prior_state",
            "new_state",
            "reason",
        ):
            if not isinstance(event.get(field), str) or not event[field].strip():
                add_error(errors, label, f"requires non-empty {field}")
        kind = str(event.get("event", ""))
        finding_id = str(event.get("finding_id", ""))
        if kind not in ALLOWED_LEDGER_EVENTS:
            add_error(errors, label, f"invalid event {kind!r}")
        if finding_id not in finding_ids and finding_id not in allowed_special_ids:
            add_error(errors, label, f"unknown finding_id {finding_id!r}")
        if event.get("proposal_hash") not in proposal_hashes:
            add_error(errors, label, "proposal_hash is not a pinned proposal input hash")
        validate_evidence_objects(event.get("evidence"), label, errors)
        if not valid_event_transition(event):
            add_error(
                errors,
                label,
                f"invalid lifecycle transition for {kind!r}: {event.get('prior_state')!r} -> {event.get('new_state')!r}",
            )
        if finding_id in current_state and event.get("prior_state") != current_state[finding_id]:
            add_error(
                errors,
                label,
                f"prior_state does not match previous ledger state {current_state[finding_id]!r}",
            )
        elif finding_id in finding_ids and finding_id not in current_state and kind != "created":
            add_error(errors, label, "first event for a review finding must be created")
        current_state[finding_id] = str(event.get("new_state", ""))
        if finding_id in finding_ids:
            seen_findings.add(finding_id)
        events_by_key.setdefault((kind, finding_id), []).append(event)

        try:
            timestamp = datetime.fromisoformat(str(event.get("timestamp", "")).replace("Z", "+00:00"))
        except ValueError:
            add_error(errors, label, "timestamp must be ISO 8601")
        else:
            if timestamp.tzinfo is None:
                add_error(errors, label, "timestamp must include a timezone")
            else:
                if prior_timestamp is not None and timestamp < prior_timestamp:
                    add_error(errors, label, "timestamps must be non-decreasing in append order")
                prior_timestamp = timestamp

    missing = sorted(finding_ids - seen_findings)
    if missing:
        add_error(errors, path.name, f"missing ledger events for findings: {', '.join(missing)}")
    return event_count, events_by_key


def crosscheck_panel_ledger(
    rating_changes: list[dict[str, Any]],
    chair_claims: list[dict[str, Any]],
    events_by_key: dict[tuple[str, str], list[dict[str, Any]]],
    label: str,
    errors: list[str],
) -> None:
    for change in rating_changes:
        if not isinstance(change, dict):
            continue
        key = f"rating:{change.get('reviewer_id', '')}"
        events = events_by_key.get(("rating_changed", key), [])
        if len(events) != 1:
            add_error(
                errors,
                label,
                f"expected exactly one rating_changed ledger event for {key}",
            )
        elif (
            events[0].get("prior_state") != change.get("initial")
            or events[0].get("new_state") != change.get("revised")
        ):
            add_error(errors, label, f"rating_changed ledger states do not match panel for {key}")
    declared_rating_ids = {
        f"rating:{change.get('reviewer_id', '')}"
        for change in rating_changes
        if isinstance(change, dict)
    }
    for kind, finding_id in events_by_key:
        if kind == "rating_changed" and finding_id not in declared_rating_ids:
            add_error(errors, label, f"ledger rating change is absent from panel: {finding_id}")
    for claim in chair_claims:
        if not isinstance(claim, dict):
            continue
        claim_id = str(claim.get("id", ""))
        events = events_by_key.get(("chair_claim_verified", claim_id), [])
        if len(events) != 1:
            add_error(
                errors,
                label,
                f"expected exactly one chair_claim_verified ledger event for {claim_id}",
            )
        elif events[0].get("new_state") != claim.get("verification_status"):
            add_error(
                errors,
                label,
                f"chair claim ledger status does not match panel for {claim_id}",
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("single-review", "review-gate", "full-panel"), default="single-review")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--review", action="append", required=True)
    parser.add_argument("--panel")
    parser.add_argument("--ledger")
    parser.add_argument("--artifact-manifest")
    parser.add_argument("--json-out")
    parser.add_argument("--minimum-reviews", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = Path(args.manifest).resolve()
    review_paths = [Path(path).resolve() for path in args.review]
    panel_path = Path(args.panel).resolve() if args.panel else None
    ledger_path = Path(args.ledger).resolve() if args.ledger else None
    run_manifest_path = Path(args.artifact_manifest).resolve() if args.artifact_manifest else None
    try:
        manifest = load_json(manifest_path)
        reviews = [(path, load_json(path)) for path in review_paths]
        panel = load_json(panel_path) if panel_path else None
        run_manifest = load_json(run_manifest_path) if run_manifest_path else None
        individual_schema, panel_schema, calibration_schema = load_contract_schemas()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    minimum_reviews = args.minimum_reviews
    if minimum_reviews is None:
        minimum_reviews = 3 if args.mode in {"review-gate", "full-panel"} else 1
    if minimum_reviews < 1:
        add_error(errors, "arguments", "--minimum-reviews must be at least 1")
    if args.mode in {"review-gate", "full-panel"} and minimum_reviews < 3:
        add_error(errors, "arguments", "review-gate/full-panel requires at least three reviews")
    if len(reviews) < minimum_reviews:
        add_error(
            errors,
            "reviews",
            f"received {len(reviews)} reviews; at least {minimum_reviews} required",
        )
    if args.mode == "full-panel":
        if panel is None or panel_path is None:
            add_error(errors, "arguments", "full-panel mode requires --panel")
        if ledger_path is None:
            add_error(errors, "arguments", "full-panel mode requires --ledger")
        if run_manifest is None or run_manifest_path is None:
            add_error(errors, "arguments", "full-panel mode requires --artifact-manifest")

    expected_hashes, proposal_hashes, authority_paths = validate_manifest_files(manifest, errors)
    proposal_id = validate_manifest_metadata(manifest, args.mode, errors, warnings)

    reviewer_ids: set[str] = set()
    reviewer_profile_ids: list[str] = []
    reviewer_backgrounds: list[str] = []
    reviewer_route_ids: list[str] = []
    model_to_families: dict[str, set[str]] = {}
    review_hashes: dict[str, str] = {}
    all_findings: dict[str, dict[str, Any]] = {}
    initial_ratings: dict[str, str] = {}
    review_additional_criteria: list[set[tuple[str, str]]] = []
    for path, review in reviews:
        label = path.name
        findings = validate_review(
            review,
            label,
            individual_schema,
            expected_hashes,
            proposal_id,
            errors,
            warnings,
        )
        review_additional_criteria.append(additional_criterion_keys(review))
        reviewer_profile = review.get("reviewer_profile")
        if isinstance(reviewer_profile, dict):
            profile_id = str(reviewer_profile.get("profile_id", "")).strip()
            if profile_id:
                reviewer_profile_ids.append(profile_id)
            simulated_background = str(
                reviewer_profile.get("simulated_background", "")
            ).strip()
            if simulated_background:
                reviewer_backgrounds.append(simulated_background)
        reviewer_route = review.get("reviewer_route")
        if isinstance(reviewer_route, dict):
            route_id = str(reviewer_route.get("route_id", "")).strip()
            if route_id:
                reviewer_route_ids.append(route_id)
        reviewer_model = str(review.get("reviewer_model", "")).strip()
        reviewer_family = str(review.get("reviewer_family", "")).strip()
        if reviewer_model and reviewer_family:
            model_to_families.setdefault(reviewer_model, set()).add(reviewer_family)
        reviewer_id = str(review.get("reviewer_id", "")).strip()
        if reviewer_id:
            if reviewer_id in reviewer_ids:
                add_error(errors, label, f"duplicate reviewer_id {reviewer_id!r}")
            reviewer_ids.add(reviewer_id)
            review_hashes[reviewer_id] = sha256_file(path)
            rating = review.get("rating")
            initial_ratings[reviewer_id] = (
                str(rating.get("value", "unrated")) if isinstance(rating, dict) else "unrated"
            )
        for finding_id, finding in findings.items():
            if finding_id in all_findings:
                add_error(errors, label, f"finding ID is not panel-unique: {finding_id!r}")
            all_findings[finding_id] = finding

    for reviewer_model, families in sorted(model_to_families.items()):
        if len(families) > 1:
            add_error(
                errors,
                "reviews",
                f"reviewer_model {reviewer_model!r} maps to multiple families: "
                + ", ".join(sorted(families)),
            )

    if args.mode in {"review-gate", "full-panel"}:
        if len(reviews) != 3:
            add_error(errors, "reviews", "review-gate/full-panel requires exactly three reviews")
        profile_counts = {
            profile_id: reviewer_profile_ids.count(profile_id)
            for profile_id in REQUIRED_REVIEWER_PROFILES
        }
        if set(reviewer_profile_ids) != REQUIRED_REVIEWER_PROFILES or any(
            count != 1 for count in profile_counts.values()
        ):
            add_error(
                errors,
                "reviews",
                "review-gate/full-panel requires exactly one reviewer profile each: "
                "general_cs, adjacent_cise, domain_methods",
            )
        if len(reviewer_backgrounds) != 3 or len(set(reviewer_backgrounds)) != 3:
            add_error(
                errors,
                "reviews",
                "review-gate/full-panel requires three distinct simulated backgrounds",
            )
        if len(reviewer_route_ids) != 3 or len(set(reviewer_route_ids)) != 3:
            add_error(
                errors,
                "reviews",
                "review-gate/full-panel requires three distinct reviewer route IDs",
            )

    expected_additional_criteria = set().union(*review_additional_criteria)
    if args.mode in {"review-gate", "full-panel"} and review_additional_criteria:
        first_criteria = review_additional_criteria[0]
        if any(criteria != first_criteria for criteria in review_additional_criteria[1:]):
            add_error(
                errors,
                "reviews",
                "sealed reviews do not contain one consistent additional-criteria set",
            )

    expected_disagreement_keys: set[tuple[str, str]] = set()
    if panel is not None:
        try:
            mechanical_aggregate = aggregate_reviews(
                reviews, generated_at="1970-01-01T00:00:00Z"
            )
        except (KeyError, TypeError, ValueError) as exc:
            add_error(errors, "reviews", f"cannot derive disagreement coverage: {exc}")
        else:
            expected_disagreement_keys = {
                (str(item.get("topic", "")), str(item.get("kind", "")))
                for item in mechanical_aggregate.get(
                    "disagreements_requiring_chair_review", []
                )
                if isinstance(item, dict)
            }

    artifact_records: dict[str, dict[str, Any]] = {}
    human_calibration_passed = False
    if (
        args.mode == "full-panel"
        and run_manifest is not None
        and run_manifest_path is not None
        and panel_path is not None
        and ledger_path is not None
    ):
        expected_model_families = {
            str(review.get("reviewer_family", "")).strip()
            for _, review in reviews
            if str(review.get("reviewer_family", "")).strip()
        }
        expected_model_ids = {
            str(review.get("reviewer_model", "")).strip()
            for _, review in reviews
            if str(review.get("reviewer_model", "")).strip()
        }
        if isinstance(panel, dict):
            chair = panel.get("chair")
            if isinstance(chair, dict) and str(chair.get("family", "")).strip():
                expected_model_families.add(str(chair["family"]).strip())
            if isinstance(chair, dict) and str(chair.get("model", "")).strip():
                expected_model_ids.add(str(chair["model"]).strip())
        artifact_records, human_calibration_passed = validate_artifact_manifest(
            run_manifest,
            run_manifest_path,
            manifest_path,
            proposal_id,
            authority_paths,
            reviews,
            review_paths,
            review_hashes,
            panel_path,
            ledger_path,
            calibration_schema,
            expected_model_families,
            expected_model_ids,
            errors,
        )

    chair_route_trusted = True
    if isinstance(panel, dict):
        chair = panel.get("chair")
        chair_route_trusted = (
            isinstance(chair, dict)
            and chair.get("provenance_source")
            in {"runtime_metadata", "human_attestation"}
        )
    derived_assurance = derive_assurance(
        [review for _, review in reviews],
        human_calibration_passed,
        chair_route_trusted,
    )
    rating_changes: list[dict[str, Any]] = []
    chair_claims: list[dict[str, Any]] = []
    if panel is not None and panel_path is not None:
        rating_changes, chair_claims = validate_panel(
            panel,
            panel_path.name,
            panel_schema,
            proposal_id,
            reviewer_ids,
            set(reviewer_route_ids),
            model_to_families,
            review_hashes,
            all_findings,
            initial_ratings,
            expected_additional_criteria,
            expected_disagreement_keys,
            derived_assurance,
            args.mode == "full-panel",
            errors,
            warnings,
        )

    ledger_event_count = 0
    if ledger_path is not None:
        chair_claim_ids = {
            str(claim.get("id", "")) for claim in chair_claims if isinstance(claim, dict)
        }
        ledger_event_count, events_by_key = validate_ledger(
            ledger_path,
            proposal_hashes,
            set(all_findings),
            reviewer_ids,
            chair_claim_ids,
            errors,
        )
        crosscheck_panel_ledger(
            rating_changes, chair_claims, events_by_key, ledger_path.name, errors
        )

    result = {
        "schema_version": "1.1",
        "mode": args.mode,
        "verdict": "FAIL" if errors else ("WARN" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "proposal_id": proposal_id,
        "packet_manifest_hash": sha256_file(manifest_path),
        "validated_review_hashes": dict(sorted(review_hashes.items())),
        "review_count": len(reviews),
        "simulated_profile_distribution": {
            profile_id: reviewer_profile_ids.count(profile_id)
            for profile_id in sorted(set(reviewer_profile_ids))
        },
        "artifact_count": len(artifact_records),
        "ledger_event_count": ledger_event_count,
        "derived_assurance": derived_assurance,
        "notice": "This verdict covers structural contracts, provenance, freshness, and completeness; it does not establish semantic reviewer correctness.",
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.json_out:
        output_path = Path(args.json_out).resolve()
        protected = {
            manifest_path,
            *review_paths,
            *(path for path in (panel_path, ledger_path, run_manifest_path) if path is not None),
        }
        manifest_files = manifest.get("files")
        if isinstance(manifest_files, list):
            protected.update(
                Path(str(record.get("absolute_path", ""))).resolve()
                for record in manifest_files
                if isinstance(record, dict) and record.get("absolute_path")
            )
        if isinstance(run_manifest, dict):
            run_artifacts = run_manifest.get("artifacts")
            if isinstance(run_artifacts, list):
                protected.update(
                    Path(str(record.get("absolute_path", ""))).resolve()
                    for record in run_artifacts
                    if isinstance(record, dict) and record.get("absolute_path")
                )
        if output_path in protected:
            print("error: --json-out cannot overwrite a validated input", file=sys.stderr)
            return 2
        atomic_text_write(output_path, rendered)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
