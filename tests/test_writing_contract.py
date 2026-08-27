"""Behavioral contract for the intentionally small Writer guidance."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "rka-writer"


def _read(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8")


def test_entrypoint_preserves_writing_freedom_and_grounding() -> None:
    text = _read("SKILL.md")
    flattened = " ".join(text.split())

    assert "The evidence constrains what can be claimed" in text
    assert "does not dictate sentence order or paragraph structure" in text
    assert "Never translate journals, claims, or database records into prose one by one" in flattened
    assert "Form the discourse plan" in text
    assert "Draft with language freedom" in text
    assert "Ground after drafting" in text


def test_entrypoint_targets_plain_domain_appropriate_language() -> None:
    text = _read("SKILL.md")
    flattened = " ".join(text.split())

    assert "plain academic language" in text
    assert "Define a project-specific term before its first use" in text
    assert "researcher-selected related works" in flattened
    assert "do not copy their sentences" in text
    assert "pre-trained" in text
    assert "Domain reminders for CS, AI, and security" in text


def test_entrypoint_stays_concise() -> None:
    line_count = len(_read("SKILL.md").splitlines())
    assert 100 <= line_count <= 220


def test_optional_references_are_short_advice_not_a_state_machine() -> None:
    references = sorted((SKILL / "references").glob("*.md"))
    assert [path.name for path in references] == [
        "discourse_synthesis.md",
        "latex_audit.md",
        "manuscript_review.md",
        "persuasive_framing.md",
    ]
    for path in references:
        text = path.read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 90, path.name
        assert ".planning/" not in text
        assert "rka writer " not in text.lower()
        assert "validate_discourse_artifacts" not in text


def test_removed_runtime_guidance_is_not_distributed() -> None:
    forbidden = (
        "rka-writer-tools",
        "validate_reference",
        "RKA_CLAIM_SPINE",
        "rka writer init",
        "rka writer sync",
        "rka writer assist",
    )
    for root in (
        SKILL,
        ROOT / "claude-plugin" / "skills" / "rka-writer",
    ):
        corpus = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".json", ".py"}
        )
        for token in forbidden:
            assert token not in corpus
