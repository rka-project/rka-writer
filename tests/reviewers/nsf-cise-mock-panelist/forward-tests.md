# Forward-test scenarios for audience and depth behavior

These synthetic passages test semantic behavior that deterministic schemas cannot establish. Run them with fresh reviewers who receive the skill normally; do not tell the reviewer which defect is planted. A pass requires evidence-grounded findings with correct severity, audience, revision type, and a useful verification test. Exact wording is not required.

## F01: jargon wall with uncertain substance

> We instantiate a qualification-contingent retained-resource lattice whose residual-energy closure induces counterfactually stable observability over the hybrid attack surface. The resulting epistemic monitor operationalizes semantic reachability under partial actuation.

Expected behavior:

- General-CS accessibility is `weak`; the reviewer identifies the first undefined load-bearing construct rather than merely counting long words.
- The reviewer does not infer novelty or technical validity from specialized language.
- The repair asks for a plain problem/insight/claim bridge before formal terminology, plus stable definitions.

## F02: clear but technically shallow

> We will build a detector that finds cyberattacks on autonomous vehicles. We will compare its accuracy with existing detectors on realistic data. If our accuracy is higher, the approach succeeds.

Expected behavior:

- Sentence-level readability is `strong`, but the full general-CS accessibility gate is `weak` because the precise gap, central idea, decisive test, and expected knowledge cannot be reconstructed.
- Expert depth is `weak`: assets, adversary, attack classes, data provenance, prevalence, baselines, operating point, false-positive cost, uncertainty, and a discriminating mechanism test are absent.
- The reviewer does not praise simplicity as a substitute for a decisive evaluation.

## F03: overloaded terminology

> The controller state determines whether the system enters a safe state. We estimate state from the state of each sensor, and the state metric is our primary outcome.

Expected behavior:

- The terminology ledger separates controller state, safety condition, sensor reading/status, and outcome metric.
- The issue is classified as reviewer friction or a confidence-lowering defect depending on surrounding definitions, not automatically as a fatal scientific flaw.

## F04: mechanism overclaim

> We observe that runs classified as high residual energy have fewer safety violations. This establishes that residual energy prevents unsafe behavior and will generalize to unseen attacks.

Expected behavior:

- The reviewer states plainly that association does not establish prevention or generalization.
- The technical basis identifies confounding or selection alternatives and the missing intervention, matched ablation, or out-of-distribution test.
- The revision type is new analysis, new evidence, or study redesign, not prose clarification alone.

## F05: throughput arithmetic defect

> Two hundred devices each emit a 2 KB record at 10 Hz. A 30-day deployment therefore produces approximately 104 GB, which fits easily in the allocated 200 GB store.

Expected behavior:

- The integrity sweep catches that the stated assumptions imply roughly 10.4 TB using decimal units, before protocol overhead, not 104 GB.
- The issue is a feasibility and reviewer-confidence concern with shown arithmetic and a request to reconcile rate, retention, compression, or storage.

## F06: deep example obscures the general claim

> Consider CAN identifier 0x1A6, whose third payload byte saturates after arbitration loss while ECU-B's diagnostic session is in subfunction 0x02. We encode this transition as edge type rho-17. Our contribution is a general method for learning invariant violations in cyber-physical systems.

Expected behavior:

- The reviewer asks why the example is necessary and which general concept each detail illustrates.
- The repair keeps only essential mechanics, first states the general problem and intuition, and explicitly reconnects the example to the claimed general method.

## F07: correct ingredients in the wrong order

> Section 3 defines twelve symbols and four loss terms. Section 4 describes an estimator. Section 5 finally explains that current monitors cannot distinguish malicious interventions from benign disturbances and that the estimator targets this gap.

Expected behavior:

- The reviewer recognizes that the content may be technically present but diagnoses navigation and progressive-exposition failure.
- The repair moves the problem, gap, intuition, and claim-to-test roadmap before notation; it does not demand removal of necessary formal detail.

## F08: clean dual-audience control

> Networked controllers can react similarly to a malicious command and to an ordinary disturbance, so a detector that uses only output deviation may confuse the two. We hypothesize that the energy required to reconcile commands with measured physical response provides an additional signal. Aim 1 defines this signal and its assumptions. Aim 2 compares it with parameter-matched deviation detectors under the same attacks and disturbances. The central claim is supported only if the energy signal improves preregistered detection at the same false-alarm rate and the gain disappears when the physical-consistency term is ablated. Null results will identify operating regimes in which physical evidence adds no information.

Expected behavior:

- The reviewer reconstructs the problem, gap, intuition, aims, decisive tests, and null-result knowledge accurately.
- Accessibility and expert depth are at least `adequate` for this bounded passage.
- The reviewer may identify genuinely unavailable proposal-level details, but does not invent a wording or methods defect merely to populate weakness fields.

## F09: rule dump duplicates a table

> A candidate episode is retained only if the source is authenticated, all seven sensor channels are present, the interval exceeds 30 seconds, fewer than two timestamps are missing, the controller remains in automatic mode, the operating range stays between 40 and 80 percent, the maintenance flag is false, and no calibration event occurs. Table 2 then lists the same eight conditions, thresholds, and exceptions in separate rows.

Expected behavior:

- The reviewer identifies duplicated decision logic and high rule load as reviewer friction rather than assuming that the rules are scientifically invalid.
- The repair keeps the decision and rationale in prose, moves operational details to the table, and checks that the two representations cannot drift.
- The reviewer requests scientific justification separately for any load-bearing threshold; reorganization alone does not validate it.

## F10: vivid example without a general bridge

> At 02:14, pump P-203 continued drawing current while its discharge pressure fell and valve V-17 reported closed. The historian preserved a 220 ms timing offset, and the safety controller entered state S4. We will use this episode to transform cyber-physical security.

Expected behavior:

- The reviewer recognizes that the scene is concrete but cannot reconstruct the general problem, inferential object, claimed contribution, or scope from it.
- The repair adds a plain general claim before or immediately after the scene and states which details instantiate that claim; it does not demand more plant-specific detail.

## F11: fuzzy central scientific object

> Our capability profile improves evaluator quality and enables robust adaptation across complex systems. We learn the profile from observations and use it throughout all three aims.

Expected behavior:

- The reviewer asks what the profile is, what inputs or evidence it is given, what operation or inference it performs, and where its validity ends.
- “Define capability profile” alone is not an adequate repair; the verification test must make the four slots reconstructable and consistent across aims.
- The reviewer does not infer a scientific flaw beyond the passage unless proposal evidence supports one.

## F12: necessary qualification, not evasive hedging

> Under bounded process noise, the proposed statistic is expected to distinguish the specified command-injection attacks from the modeled benign disturbances when the physical response remains observable. We will test where this separation fails as noise, delay, and unmodeled dynamics increase.

Expected behavior:

- The reviewer preserves the assumptions, attack scope, observability condition, and planned boundary test rather than deleting them as hedging.
- A clarity repair may make the main claim easier to see, but must not turn the statement into universal detection or guaranteed success.

## F13: a clarity edit creates an overclaim

Original:

> In the evaluated operating regimes, residual energy is associated with fewer missed detections after controlling for attack intensity; the matched intervention in Aim 2 will test whether physical consistency supplies the additional information.

Proposed edit:

> Residual energy prevents missed detections because physical consistency always reveals attacks.

Expected behavior:

- The reviewer rejects the proposed edit as a scientific-precision regression despite its shorter surface form.
- The explanation identifies the lost scope, association-versus-causation boundary, planned test, and unjustified universal quantifier.

## F14: author-house-style-only deviation

Author contract excerpt:

> Prefer commas or periods to em dashes, and avoid “not X but Y” contrast constructions.

Passage:

> The study asks whether a physical-consistency signal adds information beyond output deviation—not whether every disturbance can be classified perfectly. The claim is supported only if the preregistered, parameter-matched comparison improves detection at the same false-alarm rate.

Expected behavior:

- In the proposal-only pass, the reviewer recognizes a clear, bounded claim and decisive test.
- In the contract-aware pass, the reviewer may flag the punctuation/contrast preference and offer a meaning-preserving edit, but does not lower merit, accessibility, or technical-integrity assessments merely for house style.

## F15: correctly staged specialist detail

> A malicious command and an ordinary disturbance can produce similar output deviation, so output-only monitors may confuse them. We therefore test whether the minimum input energy needed to reconcile the command with the measured response supplies additional information. Formally, for state estimate \(x_t\), command \(u_t\), and observation \(y_t\), Aim 1 estimates \(E_t = \min_{w_{1:t}} \sum_{k=1}^{t}\|w_k\|_Q^2\) subject to the stated dynamics and observability assumptions.

Expected behavior:

- The reviewer recognizes that the passage provides a plain problem/intuition bridge before the formal definition.
- Necessary formal detail is preserved. Any critique must identify an actual undefined symbol, missing assumption, or scientific issue rather than penalizing depth itself.

## F16: stale version-specific style contract

Author contract excerpt:

> For the current four-aim, 12-page description, preview all four aims in the final introduction paragraph and reserve one page for Aim 4 transition activities.

Current proposal evidence:

> The current version is a 15-page description with three research aims; the former Aim 4 material has been removed.

Expected behavior:

- The reviewer records the supplied rule as stale or superseded and does not require a nonexistent fourth aim or impose the old space allocation.
- Transferable principles, such as giving the reader an aim roadmap, may still be offered as advisory guidance if the current proposal needs them.
- Staleness is visible in the audit trace rather than silently ignored.

## Evaluation record

For each fresh run, record skill hash, model route/family, date, scenario IDs, findings, missed planted defects, false positives on F08 and the other clean/bounded controls, severity errors, contract-contamination errors, and whether the proposed repair would actually resolve the issue without changing the science. These scenarios are regression probes, not qualified-human calibration and not evidence that semantic review is correct.
