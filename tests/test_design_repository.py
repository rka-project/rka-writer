"""Repository integrity checks, not Writer runtime or semantic validation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "docs" / "adr"
PROTECTED_SOURCE = "docs/rka-writer-authoring-ir-and-convergence-protocol.md"
ADR_STATUSES = {"Proposed", "Accepted", "Rejected", "Deprecated", "Superseded"}


def markdown_files() -> list[Path]:
    """Include pending docs locally, but exclude ignored private source material."""
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.md",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({ROOT / name for name in result.stdout.split("\0") if name})


def outside_fences(text: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            lines.append(line)
    assert fence is None, "Unclosed Markdown code fence"
    return "\n".join(lines)


def adr_status(path: Path) -> str:
    match = re.search(r"^- Status: (\w+)\s*$", path.read_text(), re.MULTILINE)
    assert match, f"{path.name}: missing status"
    assert match.group(1) in ADR_STATUSES, f"{path.name}: invalid status"
    return match.group(1)


def test_design_entrypoints_exist() -> None:
    for relative in (
        "README.md",
        "STATUS.md",
        "ROADMAP.md",
        "CONTRIBUTING.md",
        "docs/adr/README.md",
        "docs/rfcs/README.md",
        "docs/evaluation/w0-walkthrough.md",
        "docs/evaluation/w1-fixture-spec.md",
        "docs/evaluation/w1-acceptance-criteria.md",
    ):
        assert (ROOT / relative).is_file(), relative


def test_markdown_relative_links_and_fences() -> None:
    failures: list[str] = []
    for path in markdown_files():
        source = outside_fences(path.read_text(encoding="utf-8"))
        for match in re.finditer(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", source):
            raw = match.group(1).strip()
            target = raw[1 : raw.index(">")] if raw.startswith("<") else raw.split()[0]
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not failures, "\n".join(failures)


def test_adr_index_matches_records_and_supersession_is_acyclic() -> None:
    records = {path.name: path for path in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")}
    index = (ADR_DIR / "README.md").read_text()
    rows = re.findall(r"\| \[\d{4}\]\(([^)]+)\) \| (\w+) \|", index)
    assert len(rows) == len(dict(rows)), "Duplicate ADR index entries"
    assert set(dict(rows)) == set(records), "ADR index and files diverge"
    for name, status in rows:
        assert adr_status(records[name]) == status, name

    successors: dict[str, str] = {}
    for name, path in records.items():
        if adr_status(path) == "Superseded":
            match = re.search(
                r"^- Superseded by: \[[^]]+\]\(([^)]+)\)",
                path.read_text(),
                re.MULTILINE,
            )
            assert match, f"{name}: no successor link"
            assert match.group(1) in records, f"{name}: missing successor"
            successors[name] = match.group(1)
    for name in successors:
        visited: set[str] = set()
        cursor = name
        while cursor in successors:
            assert cursor not in visited, f"ADR supersession cycle at {cursor}"
            visited.add(cursor)
            cursor = successors[cursor]
        assert adr_status(records[cursor]) == "Accepted", f"{name}: no active endpoint"


def test_protected_researcher_source_is_not_tracked() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "--", PROTECTED_SOURCE],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert not tracked.stdout.strip(), "Private design source entered Git"
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", PROTECTED_SOURCE],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ignored.returncode == 0, "Private design source must stay ignored"


def test_legacy_plugin_is_not_active_and_import_remains_recoverable() -> None:
    for relative in (".claude-plugin", ".codex-plugin", "claude-plugin", "skills"):
        assert not (ROOT / relative).exists()
    legacy = ROOT / "legacy" / "core-import-v1"
    for relative in (
        "rka_writer_staging.py",
        "contracts/rka-legacy-writer-export-v1.json",
        "tests/legacy_writer_export_v1.zip.b64",
    ):
        assert (legacy / relative).is_file()


def test_superseded_design_is_preserved_as_history() -> None:
    history = ROOT / "docs" / "history" / "platform-design-v0.md"
    assert history.is_file()
