"""Repository-level contracts for the W0 design phase."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_design_stage_entrypoints_exist() -> None:
    required = [
        "README.md",
        "STATUS.md",
        "ROADMAP.md",
        "CONTRIBUTING.md",
        "docs/vision.md",
        "docs/principles.md",
        "docs/glossary.md",
        "docs/rfcs/0001-authoring-ir-and-convergence-protocol.md",
        "docs/architecture/authoring-graph.md",
        "docs/evaluation/w1-acceptance-criteria.md",
    ]
    assert [path for path in required if not (ROOT / path).is_file()] == []


def test_foundational_adrs_are_accepted() -> None:
    adrs = sorted((ROOT / "docs" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md"))
    assert len(adrs) == 4
    for adr in adrs:
        assert "- Status: Accepted" in adr.read_text(encoding="utf-8")


def test_legacy_plugin_is_not_the_active_product_surface() -> None:
    for path in (".claude-plugin", ".codex-plugin", "claude-plugin", "skills"):
        assert not (ROOT / path).exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "W0 design phase" in readme
    assert "writer-skill-v0.2.0" in readme


def test_legacy_import_remains_recoverable() -> None:
    legacy = ROOT / "legacy" / "core-import-v1"
    assert (legacy / "rka_writer_staging.py").is_file()
    assert (legacy / "contracts" / "rka-legacy-writer-export-v1.json").is_file()
    assert (legacy / "tests" / "legacy_writer_export_v1.zip.b64").is_file()


def test_superseded_design_is_preserved_as_history() -> None:
    history = (ROOT / "docs" / "history" / "platform-design-v0.md").read_text(
        encoding="utf-8"
    )
    assert "Status: Superseded in part" in history
