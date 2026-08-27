# RKA Writer

RKA Writer is an explicit-only academic manuscript drafting skill. It keeps a
small writing method separate from RKA Core so ordinary research retrieval,
coding, and project maintenance never receive manuscript-writing instructions.

## Invocation boundary

Installing the plugin makes `$rka-writer` available; it does not activate the
skill automatically. Invoke it only for manuscript drafting or revision. The
distribution contains no RKA Core MCP server, hooks, session-start command, or
agent-role bootstrap.

RKA Core is optional. Writer can work from files, URLs, repositories, and other
evidence supplied by the researcher. To use an existing RKA Core instance as an
evidence source, copy the opt-in example in
[`compatibility/core-mcp.json`](compatibility/core-mcp.json) into the host's
local MCP configuration. The example is not loaded by this plugin.

## Installation

For Codex, install this repository as a personal plugin, then invoke
`$rka-writer` only in a task where manuscript help is wanted.

For Claude Code, add this repository as a local marketplace and install
`rka-writer@rka-writer`. Its host-specific entrypoint is user-invocable and
disables model-driven activation, so installation alone does not change
ordinary research or coding sessions.

## Layout

- `skills/rka-writer/`: the canonical Codex skill and asset tree
- `claude-plugin/`: the isolated Claude plugin root; it carries Claude's
  explicit-invocation frontmatter and a mechanically mirrored asset tree
- `compatibility/core-mcp.json`: optional RKA Core connection example
- `tests/`: writing-contract and distribution-boundary tests

The original Core-coupled `rka writer` CLI wrapper, manuscript workflow engine,
Writer-specific MCP server, mandatory planning artifacts, and automatic
session-start integration are intentionally not shipped. The plugin leaves
paragraph formation and prose realization to the language model while keeping
claims grounded in researcher-provided evidence.

## Development

```bash
python -m pip install -r requirements-dev.txt
pytest
```

Plugin and skill metadata can be checked with the Codex `plugin-creator` and
`skill-creator` validators.
