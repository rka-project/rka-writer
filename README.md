# RKA Writer

RKA Writer is an explicit-only academic writing and review plugin. It keeps a
small drafting method separate from RKA Core and keeps advisory reviewer
contexts separate from drafting, so ordinary research retrieval, coding,
project maintenance, and prose generation do not receive unrelated instructions.

## Invocation boundary

Installing the plugin makes four explicit-only skills available; it activates
none of them automatically:

The `$...` names below show Codex syntax; Claude Code commands are listed under
Installation.

- `$rka-writer` for manuscript drafting and revision;
- `$ai-cyber-paper-reviewer` for read-only AI, cybersecurity, and related CS
  paper review;
- `$nsf-cise-mock-panelist` for read-only mock review of proposer-owned NSF CISE
  proposals; and
- `$holistic-academic-reviewer` to route an explicitly requested review to the
  correct specialist.

The distribution contains no RKA Core MCP server, hooks, session-start command,
or agent-role bootstrap. Reviewers are not automatic Writer gates. See
[`docs/reviewer-integration.md`](docs/reviewer-integration.md) for the phase
boundary and handoff design.

RKA Core is optional. Writer can work from files, URLs, repositories, and other
evidence supplied by the researcher. To use an existing RKA Core instance as an
evidence source, copy the opt-in example in
[`compatibility/core-mcp.json`](compatibility/core-mcp.json) into the host's
local MCP configuration. The example is not loaded by this plugin.

## Installation

For Codex, install this repository as a personal plugin, then invoke the one
skill needed for the current drafting or review task.

Codex entrypoints are `$rka-writer`, `$ai-cyber-paper-reviewer`,
`$nsf-cise-mock-panelist`, and `$holistic-academic-reviewer`.

For Claude Code, add this repository as a local marketplace and install
`rka-writer@rka-writer`. Every host-specific entrypoint is user-invocable and
disables model-driven activation, so installation alone does not change
ordinary research, coding, or writing sessions.

Claude Code entrypoints are `/rka-writer:rka-writer`,
`/rka-writer:ai-cyber-paper-reviewer`,
`/rka-writer:nsf-cise-mock-panelist`, and
`/rka-writer:holistic-academic-reviewer`.

## Layout

- `skills/`: canonical Codex trees for Writer, two specialist reviewers, and
  the Holistic router
- `claude-plugin/`: the isolated Claude plugin root; it carries Claude's
  explicit-invocation frontmatter and mechanically mirrored asset trees
- `docs/reviewer-integration.md`: context and handoff architecture
- `compatibility/core-mcp.json`: optional RKA Core connection example
- `tests/`: writing-contract, distribution-boundary, and reviewer regression
  tests

The original Core-coupled `rka writer` CLI wrapper, manuscript workflow engine,
Writer-specific MCP server, mandatory planning artifacts, and automatic
session-start integration are intentionally not shipped. The plugin leaves
paragraph formation and prose realization to the language model while keeping
claims grounded in researcher-provided evidence. Reviewer ledgers, ratings, and
adversarial language remain in separate explicitly invoked review contexts.

## Design documents

- [`docs/platform-design.md`](docs/platform-design.md) describes the proposed
  researcher-in-the-loop Paper Studio product vision, architecture, workflow,
  roadmap, and evaluation plan. It is a future design outline, not a statement
  of currently implemented behavior.
- [`docs/reviewer-integration.md`](docs/reviewer-integration.md) defines the
  context and handoff boundary between drafting and advisory reviewer skills.

## Development

```bash
python -m pip install -r requirements-dev.txt
pytest
```

Plugin and skill metadata can be checked with the Codex `plugin-creator` and
`skill-creator` validators.
