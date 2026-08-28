# Fast-Reader and Cognitive-Load Audit

Use this audit to model a busy program-committee reviewer who is a general computer-science or security expert but not necessarily a specialist in the paper's subfield. Keep the manuscript immutable. Diagnose comprehension before suggesting repairs.

## 1. Freeze the cold-read view

- Start without related work, appendices, external searches, or author explanations.
- Record exactly which pages and visual elements are accessible.
- Do not use later sections to retroactively mark an initially unclear concept as clear; record where understanding first became possible.
- If extraction, OCR, layout, or missing supplementary material limits the audit, report that limitation.

## 2. Run the 30-second reconstruction

Use only the title, abstract, and opening introduction material that a fast reviewer could reasonably scan. Reconstruct, in one sentence each:

1. the concrete problem and why it matters;
2. the protected asset or desired property and relevant attacker, if applicable;
3. the gap in prior approaches;
4. the paper's core idea in plain technical language;
5. the main evidence;
6. the claimed contribution and its boundary.

Score every item:

- `2`: explicit and accurately reconstructable;
- `1`: inferable only by combining dispersed clues or unexplained terms;
- `0`: missing, ambiguous, or likely to be reconstructed incorrectly.

Record the first comprehension breakpoint and the first point at which the paper resolves it. Treat a wrong but confident reconstruction as more serious than a visibly missing detail.

## 3. Run the three-minute navigation sweep

Scan section headings, contribution bullets, architecture or method overview, figures, tables, captions, and conclusion. Without reading the full prose, answer:

- What is built, measured, proved, attacked, or defended?
- What is the end-to-end workflow or causal chain?
- Which result supports each headline claim?
- What changes relative to the strongest baseline or closest work?
- What are the principal assumptions and limitations?
- Can a reviewer find the threat model, method, datasets, baselines, metrics, and main results without hunting?

Record missing signposts, misleading headings, captions that require body text, figures with no takeaway, and claim-to-evidence navigation failures.

## 4. Locate cognitive-load sources

Flag only observable burdens and anchor each one to the manuscript:

- undefined or late-defined terms, acronyms, symbols, actors, datasets, or security goals;
- dense noun phrases, stacked qualifiers, overloaded notation, or labels that change across sections;
- deep domain examples introduced before the general problem or invariant;
- background and contribution interleaved so the novelty boundary is hard to see;
- mechanisms presented before purpose, inputs, outputs, or threat assumptions;
- vague referents such as “this,” “it,” “the framework,” or “the attack” when several candidates exist;
- long forward references, repeated backtracking, or definitions separated from first use;
- paragraphs with multiple argumentative jobs and no clear lead sentence;
- visuals whose arrows, actors, units, legends, scales, or comparison target are unclear;
- equations or implementation details that obscure the decision-relevant intuition;
- essential qualifications deferred until evaluation or limitations;
- contribution lists that describe activities rather than new knowledge or demonstrated capability.

Do not infer AI authorship from stylistic patterns. Do not penalize legitimate technical density merely because the domain is complex; distinguish inherent conceptual difficulty from avoidable exposition cost.

## 5. Test each major section

For the abstract, introduction, overview, method/design, threat model, evaluation, related work, and conclusion, identify:

`section purpose -> question answered -> prerequisite knowledge -> main claim -> supporting evidence -> transition to next section`

Flag a section when its purpose is not evident early, prerequisites are unexplained, evidence appears before the claim, the section changes terminology, or the transition forces the reader to reconstruct the argument.

## 6. Use two comprehension lenses

- **General-expert lens:** Can a computer-science or security researcher outside the niche recover the problem, idea, stakes, and evidence without specialist examples?
- **Domain-expert lens:** Are simplified explanations still technically correct, and are assumptions, edge cases, and mechanisms precise enough for scrutiny?

Preserve disagreement between the lenses. A domain expert's successful reconstruction does not erase a generalist's failure, and accessible prose does not compensate for a shallow or incorrect technical account.

## 7. Calibrate findings

- **Critical:** the presentation failure directly creates or conceals a validity, policy, integrity, safety, or ethics failure that independently meets the Critical threshold.
- **Major:** a fast reader is likely to misunderstand the central problem, core idea, threat model, contribution, or headline evidence; or repeated backtracking, unexplained prerequisites, or poor navigation materially increases reviewer effort or weakens confidence.
- **Minor:** a local definition, sentence, caption, label, or transition creates repairable friction.

Central-idea confusion alone is `Major`, not `Critical`, even when it could strongly affect a rushed reviewer's score. For every Critical or Major finding, report: `conditional`, lifecycle `status`, manuscript anchor, reader reconstruction, intended meaning if recoverable, source of load, reviewer consequence, and smallest repair. Prefer reordering, definition, claim calibration, a plain-language invariant, or a better overview visual before adding more prose.

## 8. Convert each breakpoint into a revision suggestion

Do not stop at “unclear” or “high cognitive load.” For every material breakpoint, produce:

| Field | Required content |
|---|---|
| Conditional | `true` when incomplete or uninspected material could change the full-paper judgment; otherwise `false` |
| Status | `open`, `resolved`, or `withdrawn` |
| Exact anchor | Page/section/paragraph, heading, figure/table, caption, equation, term, or transition |
| Fast-reader action | What the reviewer must infer, remember, search for, or reread |
| Likely misreading | The incorrect or incomplete model a rushed reviewer may form |
| Load source | Ordering, missing prerequisite, terminology, notation, sentence structure, visual design, or claim-evidence navigation |
| Smallest repair | Move, define, delete, split, rename, foreground, cross-reference, add a lead sentence, or revise a visual/caption |
| Concrete suggestion | Exact content function and placement; optional illustrative wording or wireframe when useful |
| Precision guard | Technical condition, scope, or distinction the revision must preserve |
| Cold-read test | What a fresh general CS reader should reconstruct, and from which material, after the change |

Use this repair order:

1. Put the general problem, invariant, decision, or causal chain before niche terminology and deep examples.
2. Move existing definitions and qualifications to first use before adding text.
3. Give each paragraph and section one visible argumentative job with a clear lead sentence.
4. Make headings, contribution bullets, figures, tables, and captions carry the navigation path.
5. Align labels, actors, acronyms, symbols, datasets, and claims across sections.
6. Split dense sentences or equations only when the split reduces working-memory demands without hiding technical dependencies.

When suggesting wording, label it `illustrative` and check that it does not strengthen, narrow, or alter the scientific claim accidentally. When a figure is the better repair, specify the reviewer question it should answer, the required actors/data flow/trust boundary/result takeaway, and the caption's one-sentence conclusion.

If the exact technical meaning needed for a safe rewrite is not recoverable from the manuscript, use explicit functional placeholders and link the missing item to a decision-relevant post-freeze author question. Do not guess component roles, control flow, certificate semantics, threat assumptions, or causal mechanisms merely to make the prose sound fluent.

## 9. Produce a compact audit record

Include the six 30-second scores, the three-minute reconstruction, first breakpoint, backtracking count or locations, terminology/notation hotspots, strongest navigational aid, a full breakpoint-to-revision matrix, top three load-bearing presentation repairs, and confidence. Rank repairs by how much of the paper they unlock, not by how easy they are to line-edit. State `no material issue found` for tested dimensions that pass; do not invent a fixed number of weaknesses.
