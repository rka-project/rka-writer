# Repository guidance

Read `README.md`, `STATUS.md`, `ROADMAP.md`, the active RFC, and all accepted
ADRs before changing this repository.

- The active product is a researcher-controlled Authoring Graph and convergence
  workbench. It is not the frozen prose-first Writer skill.
- W0 is a design-freeze phase. Do not add an authoring runtime or UI until the
  W1 acceptance contract is stable and explicitly approved.
- Do not restore plugin distributions or Reviewer skills to the active root.
- Treat `legacy/core-import-v1/` as compatibility infrastructure, not as the
  future architecture.
- Preserve `docs/rka-writer-authoring-ir-and-convergence-protocol.md` as an
  untracked researcher design source unless the PI explicitly changes that
  instruction. The tracked RFC is its reviewable distilled artifact.
- Never generate large prose blocks without approved upstream semantic state.
  Respect dependency staleness, researcher decisions, locked terms, and the
  sentence-admission rule defined by the ADRs.
