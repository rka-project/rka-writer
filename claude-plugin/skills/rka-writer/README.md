# RKA Writer skill

This directory contains the explicit-only RKA Writer skill. Invoke it with the
host-specific command documented in the repository README. It is intentionally
small: one writing entrypoint and five
optional references, including a narrow handoff for separately frozen review
reports. It does not include a workflow engine, mandatory planning
artifacts, manuscript state machine, reference-validation service, or automatic
session role.

RKA Core is optional. Writer can use files, URLs, repositories, selected related
papers, and researcher-provided evidence directly. When Core is available, it
serves as an auditable evidence source through its public MCP contract; its
records constrain factual claims but do not determine paragraph structure.

See [`SKILL.md`](SKILL.md) for the writing method. Load a reference only when it
helps the current task.
