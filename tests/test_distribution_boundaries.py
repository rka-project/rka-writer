"""Hard boundaries for the standalone Writer distribution."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "rka-writer"


def test_host_specific_entrypoints_are_isolated_and_in_sync() -> None:
    skill_files = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.glob("**/SKILL.md"))
    assert skill_files == [
        "claude-plugin/skills/rka-writer/SKILL.md",
        "skills/rka-writer/SKILL.md",
    ]
    assert not (ROOT / "rka").exists()

    codex_skill = (SKILL / "SKILL.md").read_text()
    claude_skill = (
        ROOT / "claude-plugin" / "skills" / "rka-writer" / "SKILL.md"
    ).read_text()
    assert codex_skill.split("---", 2)[2] == claude_skill.split("---", 2)[2]


def test_plugin_manifests_expose_only_the_skill() -> None:
    codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    claude = json.loads(
        (ROOT / "claude-plugin" / ".claude-plugin" / "plugin.json").read_text()
    )
    assert codex["name"] == claude["name"] == "rka-writer"
    assert codex["skills"] == "./skills/"
    for manifest in (codex, claude):
        assert "mcpServers" not in manifest
        assert "hooks" not in manifest
        assert "commands" not in manifest


def test_claude_marketplace_points_to_standalone_plugin() -> None:
    marketplace = json.loads(
        (ROOT / ".claude-plugin" / "marketplace.json").read_text()
    )
    assert marketplace["name"] == "rka-writer"
    assert marketplace["plugins"] == [
        {
            "name": "rka-writer",
            "description": marketplace["plugins"][0]["description"],
            "author": {"name": "Chenglong Fu"},
            "category": "research",
            "source": "./claude-plugin",
        }
    ]


def test_writer_is_explicit_only_on_codex_and_claude() -> None:
    openai = yaml.safe_load((SKILL / "agents" / "openai.yaml").read_text())
    assert openai["policy"]["allow_implicit_invocation"] is False

    codex_text = (SKILL / "SKILL.md").read_text()
    codex_frontmatter = codex_text.split("---", 2)[1]
    assert "disable-model-invocation" not in codex_frontmatter

    claude_text = (
        ROOT / "claude-plugin" / "skills" / "rka-writer" / "SKILL.md"
    ).read_text()
    claude_frontmatter = claude_text.split("---", 2)[1]
    assert re.search(r"^disable-model-invocation:\s*true$", claude_frontmatter, re.MULTILINE)
    assert re.search(r"^user-invocable:\s*true$", claude_frontmatter, re.MULTILINE)
    assert codex_text.split("---", 2)[2] == claude_text.split("---", 2)[2]


def test_no_bundled_mcp_or_session_bootstrap() -> None:
    assert list(ROOT.glob(".mcp.json")) == []
    assert list(SKILL.rglob(".mcp.json")) == []
    assert not (ROOT / "hooks").exists()
    assert not (ROOT / "commands").exists()
    assert not (ROOT / "scripts" / "start-manuscript.py").exists()

    compat = json.loads((ROOT / "compatibility" / "core-mcp.json").read_text())
    assert set(compat["mcpServers"]) == {"rka"}


def test_distributed_python_has_no_core_imports() -> None:
    core_import = re.compile(r"(?m)^\s*(?:from\s+rka(?:\.|\s)|import\s+rka(?:\.|\s|$))")
    offenders = []
    for path in [*SKILL.rglob("*.py"), *(ROOT / "eval-harness").rglob("*.py")]:
        if core_import.search(path.read_text(encoding="utf-8")):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_claude_asset_mirror_matches_canonical_tree() -> None:
    claude_skill = ROOT / "claude-plugin" / "skills" / "rka-writer"
    for canonical in SKILL.rglob("*"):
        if not canonical.is_file() or canonical.name == "SKILL.md":
            continue
        relative = canonical.relative_to(SKILL)
        mirrored = claude_skill / relative
        assert mirrored.is_file(), f"missing Claude asset mirror: {relative}"
        assert mirrored.read_bytes() == canonical.read_bytes(), (
            f"Claude asset drift: {relative}"
        )
