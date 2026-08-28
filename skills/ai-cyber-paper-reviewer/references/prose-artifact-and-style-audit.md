# Prose Artifact and Style Audit

Use this pass after substantive review. Diagnose observable writing and submission-artifact problems without inferring how the prose was produced. Keep the manuscript read-only; offer author-facing examples only when useful.

## 1. Authorship-neutral rule

Never infer AI authorship from em dashes, sentence rhythm, transition phrases, vocabulary, paragraph shape, or any other stylistic pattern. Such features are not reliable provenance evidence. Report only the concrete effect on clarity, precision, consistency, credibility, or compliance.

Use labels such as `generic phrasing`, `unsupported emphasis`, `repetition`, `terminology drift`, `submission artifact`, or `citation artifact`; do not label prose `AI-written` or assign an AI probability.

## 2. Critical submission artifacts

Flag with exact locations:

- unresolved placeholders such as `[TODO]`, `[insert citation]`, or dummy values;
- internal tool tokens such as `turn0search0`, `oaicite`, `contentReference`, JSON metadata, or prompt/refusal fragments;
- malformed, fabricated-looking, or unresolved citations, DOIs, arXiv IDs, URLs, figure references, labels, or cross-references;
- author names, acknowledgments, repository identities, PDF metadata, or tracked changes that may violate the verified anonymity policy;
- contradictory manuscript versions, stale captions, missing figures, clipped equations, or source/PDF disagreement.

Do not repeat unnecessary identifying information in the report.

## 3. General-expert clarity

Check whether a general computer-science or security reviewer can recover:

- the concrete problem before niche examples;
- the asset, failure, attacker, or objective;
- the core idea in plain technical language;
- inputs, outputs, assumptions, and scope;
- which evidence supports each contribution;
- the practical meaning of the main metrics.

Flag delayed definitions, unexplained prerequisites, stacked acronyms, overloaded symbols, dense noun phrases, deep examples before invariants, and passages that require repeated backtracking. Use `fast-reader-audit.md` for the cold-read procedure.

## 4. Precision and terminology

Check that:

- terms are defined before use and retain one meaning;
- actor, component, dataset, threat, metric, and method names do not drift;
- pronouns and generic labels have unambiguous referents;
- claims state the population, setting, attacker, model, or benchmark boundary;
- causal, security, formal, and empirical verbs match the evidence;
- units, denominators, directions of improvement, and comparison targets are explicit;
- a simpler phrase is used when it preserves the technical meaning.

Do not replace a domain term merely because it is specialized. Define it, motivate it, or add intuition while preserving the exact mechanism.

## 5. Evidence-bearing prose

Flag:

- promotional superlatives without evidence;
- generic importance claims that do not identify a concrete consequence;
- claims of proof, guarantee, completeness, universality, real-world deployment, or state of the art beyond the design;
- generic transitions or section summaries that repeat rather than advance the argument;
- contribution bullets that list activities instead of new knowledge or demonstrated capability;
- paragraphs performing several argumentative jobs without a clear lead claim;
- limitations written defensively or disconnected from the headline claims.

Do not treat the rule of three, em dashes, semicolons, or polished transitions as defects by themselves. Flag them only when an anchored passage creates measurable repetition, ambiguity, or cognitive load.

## 6. Contextual claim calibration

Treat these as reasoning patterns, not mechanical substitutions:

| Risky wording | Question to resolve | Possible calibrated form |
|---|---|---|
| `proves` | Is there a proof, or only an experiment? | `shows in the evaluated setting` when empirical |
| `guarantees` | What assumptions and enforcement mechanism establish it? | `enforces under assumptions X` or `empirically reduces Y` |
| `model-agnostic` | Is the mechanism independent of model internals, or tested across families? | State the precise independence property and tested models |
| `real-world` | Was there deployment, field data, or only a realistic benchmark? | Name the actual setting |
| `state of the art` | Were current closest methods compared fairly? | Name the evaluated comparison and date |
| `robust` | Against which attackers, budgets, distributions, and failures? | State the tested threat classes and boundaries |
| `minimal overhead` | Relative to what denominator and workload? | Report measured latency, cost, or resource change |

Never change `model-agnostic` to `architecture-agnostic` unless that is the paper's actual property. Every suggested rewrite must pass a meaning-preservation check.

## 7. Review-comment contract

For each material writing finding, report:

- `conditional` (`true` or `false`) and lifecycle `status` (`open`, `resolved`, or `withdrawn`);
- exact manuscript anchor;
- the reader's likely reconstruction or confusion;
- the intended meaning, if recoverable;
- why the issue matters to the paper's argument or reviewer effort;
- the smallest repair: define, reorder, split, name, quantify, narrow, add intuition, or redesign a visual;
- a concrete placement/content suggestion and optional illustrative wording;
- the technical assumption, scope, or distinction that the revision must preserve;
- a verification test, such as successful one-sentence reconstruction by a general expert.

Prefer an actionable diagnosis over a generic edit request. Example wording is illustrative, not mandatory, and must not silently add facts or alter assumptions.

## 8. Final gate

- Keep scientific depth while reducing avoidable cognitive load.
- Distinguish language proficiency from research quality.
- Preserve legitimate author voice and venue-appropriate terminology.
- Avoid vague praise and vague criticism.
- Ensure every suggested statement is supported by the manuscript or clearly marked as a proposed clarification.
- Report `no material issue found` when a tested dimension passes.
