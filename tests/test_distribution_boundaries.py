"""Hard boundaries for the standalone Writer distribution."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SKILL = SKILLS / "rka-writer"
SKILL_NAMES = [
    "ai-cyber-paper-reviewer",
    "holistic-academic-reviewer",
    "nsf-cise-mock-panelist",
    "rka-writer",
]


def test_host_specific_entrypoints_are_isolated_and_in_sync() -> None:
    skill_files = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.glob("**/SKILL.md"))
    assert skill_files == [
        "claude-plugin/skills/ai-cyber-paper-reviewer/SKILL.md",
        "claude-plugin/skills/holistic-academic-reviewer/SKILL.md",
        "claude-plugin/skills/nsf-cise-mock-panelist/SKILL.md",
        "claude-plugin/skills/rka-writer/SKILL.md",
        "skills/ai-cyber-paper-reviewer/SKILL.md",
        "skills/holistic-academic-reviewer/SKILL.md",
        "skills/nsf-cise-mock-panelist/SKILL.md",
        "skills/rka-writer/SKILL.md",
    ]
    assert not (ROOT / "rka").exists()

    for skill_name in SKILL_NAMES:
        codex_skill = (SKILLS / skill_name / "SKILL.md").read_text()
        claude_skill = (
            ROOT / "claude-plugin" / "skills" / skill_name / "SKILL.md"
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


def test_all_skills_are_explicit_only_on_codex_and_claude() -> None:
    for skill_name in SKILL_NAMES:
        codex_root = SKILLS / skill_name
        openai = yaml.safe_load((codex_root / "agents" / "openai.yaml").read_text())
        assert openai["policy"]["allow_implicit_invocation"] is False

        codex_text = (codex_root / "SKILL.md").read_text()
        codex_frontmatter = codex_text.split("---", 2)[1]
        assert "disable-model-invocation" not in codex_frontmatter

        claude_text = (
            ROOT / "claude-plugin" / "skills" / skill_name / "SKILL.md"
        ).read_text()
        claude_frontmatter = claude_text.split("---", 2)[1]
        assert re.search(
            r"^disable-model-invocation:\s*true$", claude_frontmatter, re.MULTILINE
        )
        assert re.search(
            r"^user-invocable:\s*true$", claude_frontmatter, re.MULTILINE
        )
        assert codex_text.split("---", 2)[2] == claude_text.split("---", 2)[2]

    claude_writer = (
        ROOT / "claude-plugin" / "skills" / "rka-writer" / "SKILL.md"
    ).read_text()
    assert "/rka-writer:rka-writer" in claude_writer.split("---", 2)[1]


def test_no_bundled_mcp_or_session_bootstrap() -> None:
    assert list(ROOT.glob(".mcp.json")) == []
    assert list(SKILLS.rglob(".mcp.json")) == []
    assert not (ROOT / "hooks").exists()
    assert not (ROOT / "commands").exists()
    assert not (ROOT / "scripts" / "start-manuscript.py").exists()

    compat = json.loads((ROOT / "compatibility" / "core-mcp.json").read_text())
    assert set(compat["mcpServers"]) == {"rka"}


def test_distributed_python_has_no_core_imports() -> None:
    offenders = []
    excluded_roots = {".git", ".pytest_cache", ".ruff_cache", ".venv", "tests"}
    for path in ROOT.rglob("*.py"):
        relative = path.relative_to(ROOT)
        if any(part in excluded_roots or part == "__pycache__" for part in relative.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(relative))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name == "rka" or alias.name.startswith("rka.") for alias in node.names
            ):
                offenders.append(relative.as_posix())
                break
            if isinstance(node, ast.ImportFrom) and node.module and (
                node.module == "rka" or node.module.startswith("rka.")
            ):
                offenders.append(relative.as_posix())
                break
    assert offenders == []


def test_claude_asset_mirrors_match_canonical_trees() -> None:
    manifest = Path("assets/engine-manifest.json")
    for skill_name in SKILL_NAMES:
        canonical_root = SKILLS / skill_name
        claude_root = ROOT / "claude-plugin" / "skills" / skill_name
        canonical_files = {
            path.relative_to(canonical_root)
            for path in canonical_root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        }
        claude_files = {
            path.relative_to(claude_root)
            for path in claude_root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        }
        assert claude_files == canonical_files, f"Claude file-set drift: {skill_name}"
        for relative in sorted(canonical_files):
            if relative == Path("SKILL.md"):
                continue
            if skill_name == "holistic-academic-reviewer" and relative == manifest:
                # Claude SKILL frontmatter changes native-engine hashes, so this
                # generated manifest is intentionally host-specific.
                continue
            canonical = canonical_root / relative
            mirrored = claude_root / relative
            assert mirrored.read_bytes() == canonical.read_bytes(), (
                f"Claude asset drift: {skill_name}/{relative}"
            )


def test_holistic_router_uses_single_canonical_engine_copy() -> None:
    for skills_root in (SKILLS, ROOT / "claude-plugin" / "skills"):
        router = skills_root / "holistic-academic-reviewer"
        assert not list(router.rglob("engines"))
        manifest = json.loads((router / "assets" / "engine-manifest.json").read_text())
        assert [engine["root"] for engine in manifest["engines"]] == [
            "ai-cyber-paper-reviewer",
            "nsf-cise-mock-panelist",
        ]


def test_host_specific_holistic_manifests_are_current() -> None:
    for skills_root in (SKILLS, ROOT / "claude-plugin" / "skills"):
        script = (
            skills_root
            / "holistic-academic-reviewer"
            / "scripts"
            / "validate_academic_review.py"
        )
        result = subprocess.run(
            [sys.executable, "-B", str(script), "verify-engines", "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
