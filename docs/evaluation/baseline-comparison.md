# Baseline Comparison

The human evaluation eventually compares three conditions using the same
research material, task, venue, and—where supported—base model settings:

1. a conventional general-LLM writing prompt;
2. Writer skill 0.2 pinned at `writer-skill-v0.2.0`; and
3. the RKA Writer workbench.

## Measure four dimensions

### Scientific fidelity

Unsupported claims, claim-evidence mismatch, citation support errors,
numerical drift, omitted material counterevidence, and claim broadening.

### Convergence

Time to stable paper question and claim portfolio, reopened high-level
decisions, stale downstream artifacts, hidden inconsistency, semantic
oscillation, and cold-start recovery accuracy.

### Researcher control and effort

Consequential decisions per researcher minute, accept/edit/reject rates,
researcher edit distance, undo rate, unintended semantic changes, perceived
cognitive load, and confidence in provenance and control.

### Reader-facing quality

Quick-reader comprehension, contribution visibility, narrative coherence,
terminology clarity, naturalness, unnecessary caveat rate, and author-style
match.

Output prose quality is necessary but not sufficient. A fluent condition fails
if it hides semantic change or weakens researcher control.
