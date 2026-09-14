# Language and Revision Protocol

- Status: Proposed operational detail under ADR 0008 and RFCs 0001–0003
- Date: 2026-09-14
- Parent: [Writer framework](writer-framework-synthesis.md)
- Evidence basis: [observation ledger](../research/2026-09-14-writing-workflow-observations.md)

These are logical task contracts to test in W0/W1, not installed skills,
production schemas or permission for broad prose generation. Keep reusable
review guidance separate from manuscript mutation and from the frozen Writer
0.2 skill. A future skill routes to these contracts; it cannot enforce access
control, grant approval or replace coordinator validation by prompt alone.

## 1. Term proposal before term lock

### Inputs

The target concept, its role in the approved research question/claim, selected
field literature with locators, related concepts, current provisional labels,
reader background and any author-supplied naming preference.

Literature examples establish how a term is used in a source, not universal
consensus. A preferred paper supplies neither synonym equivalence nor automatic
permission to reuse its distinctive wording.

### Proposal fields

| Field | Question answered |
|---|---|
| Concept identity and version | What exactly is being named, independent of its label? |
| Definition and scope | What does the concept include and exclude? |
| Candidate labels and precedents | Where is each used, and in what sense? |
| Nearest contrasts | Why is this not the adjacent concept? |
| Example and counterexample | Which concrete cases delimit the distinction? |
| Recommendation and uncertainty | Why prefer one label; what remains unresolved? |
| Allowed forms | Canonical spelling, abbreviation, grammatical forms and contexts |
| Disallowed equivalences | Which substitutions would change meaning in this context? |
| First-use plan | Where is the term defined and what does the reader need first? |
| Impact and decision | Which intents/locations depend on it; who approved what version? |

Not every field needs a separate UI control. Show the meaningful contrast and
ask the researcher to select, edit, reject or defer. Permit a new term when
existing terms do not fit, with a precise definition and explicit approval.
Do not require false literature precedent for a genuinely new construct.

### Outcomes

1. Same concept, accepted label: record the scoped Term Lock and exact version.
2. New distinction or changed scope: reopen the affected scientific/discourse
   commitment before locking; do not disguise it as a lexical edit.
3. Insufficient information: record the specific question and block only
   dependent generation, not unrelated work.

Different terms can validly name different concepts. The same string can have
different senses. Exact term lint is a structural check; concept identity and
appropriate context require review. Do not globally replace aliases by regex.

## 2. Grounded expression audit, not AI detection

### Inputs and allowed outputs

Read the selected manuscript span, its paragraph/intent plan, selected evidence,
scope/qualifiers, term locks, reader contract, applicable style and nearby text.
Missing context is reported as unknown, not reconstructed as fact.

Output an anchored issue list or a justified pass. The audit cannot rewrite,
select new evidence, strengthen claims, change terms or approve itself.

Each issue records:

- issue ID, document revision and exact span/anchor;
- observed problem and category;
- source/contract basis, not merely the critic's preference;
- reader consequence and severity with uncertainty;
- proposed disposition and the responsible decision layer;
- minimal allowed repair scope and protected meaning;
- researcher question, if a consequential choice remains.

### Checks and counterexamples

| Check | A real defect | Do not flag merely because |
|---|---|---|
| Informativeness | Importance/gap language adds no setting, mechanism or consequence | A sentence provides needed orientation |
| Scope and qualification | A vague reassurance hides the actual tested boundary | A hedge preserves material uncertainty |
| Mechanism clarity | Noun chains conceal who acts on what, when and why | The field uses a precise nominal technical term |
| Term identity | Stylistic synonym substitution changes the concept | A canonical term is repeated |
| Reader path | A transition asserts an unsupported logical dependency | A transition or preview is present |
| Redundancy | Repeated framing adds no necessary information or retrieval cue | Introduction and conclusion revisit a contribution |
| Audience fit | Implementation jargon appears before the reader can connect it to the scientific task | Specialized detail is needed in Methods |
| Style fit | Wording conflicts with an applicable endorsed preference | A word, punctuation mark or rhythm seems "AI-like" |

The deletion test asks what understanding is lost, not merely whether a new
empirical fact disappears. Signposting, definitions and logical connections
can be valuable without reporting new results. Sentence-length and vocabulary-
diversity statistics are observations, not universal quality targets.

## 3. Route findings to the smallest responsible layer

| Finding | Route | Do not do |
|---|---|---|
| Unsupported scope or missing evidence | Scientific commitment | Rescue it with stronger rhetoric or an invented citation |
| Missing warrant, wrong paragraph job or duplicate reader move | Discourse plan | Hide the missing reasoning behind "therefore" |
| Concept conflation | Concept/term proposal; science if needed | Replace a word globally |
| Same-meaning clarity defect | One-intent expression proposal after admission | Rewrite the surrounding section |
| Personal preference only | Local edit or optional scoped calibration | Make it a scientific blocker or universal style rule |
| Correct and readable passage | Pass / no change | Manufacture work to satisfy a review loop |

An upstream issue may affect multiple intents. Review its plan/impact as a
bundle, then regenerate only explicitly selected admitted intents one at a time.
Read-only whole-paper inspection remains a separate, explicitly scoped route.

## 4. Calibrate author preferences without hidden learning

1. Ask which quality in a selected sample is useful and where it should apply.
2. Record a source-grounded observation or direct author preference, including
   confounders such as section type, venue conventions and technical subject.
3. Hold proposition, evidence, scope, terms and rhetorical intent fixed.
4. Show a small candidate set differing in one declared expression dimension.
5. Accept a local choice, author edit or rejection of all candidates.
6. Separately propose generalization with its scope, exceptions and examples.

Term equivalence is not a style preference. Removing "may" or adding a causal
verb may change science. A local acceptance must not automatically mutate the
profile. Check transfer on another admitted intent, not just the calibration
sentence. Whole samples remain excluded from realization; any short example
needs separate source-use approval and copy-risk review under RFC 0003.

## 5. Bound changes by their semantic effect

The surface category "grammar" or "punctuation" does not establish safety.
Only an explicit narrow mechanical policy may authorize automatic application;
meaning-uncertain changes require review. No new auto-apply policy is adopted
by this document.

A patch proposal identifies its issue IDs, exact base revisions, allowed
targets, protected spans, expected repair and applicable approval. A sentence
candidate still obeys ordinary admission. Changed bases require a fresh preview.

### Change report

Record each axis independently; `unknown` requires review:

| Axis | Examples |
|---|---|
| Scientific record | Unchanged / new claim or scope version / evidence interpretation changed |
| Expressed proposition | Preserved / restored omitted approved qualifier / narrowed / broadened / unknown |
| Evidence and citations | Selected uses unchanged / locator changed / support re-reviewed |
| Quantitative meaning | Value, metric, unit, denominator, comparator, condition, uncertainty |
| Concept and terminology | Concept unchanged / alias canonicalized / definition or distinction changed |
| Discourse and mapping | Function/order preserved or revised; anchors remapped |
| Style and authorization | Local choice only / separately approved profile rule; exact approvals used |

Example from report slide 62: restoring a previously approved condition can
leave the canonical claim unchanged while correcting what the sentence says.
Report both facts. If the condition was never approved, it is a new semantic
proposal. "Claims changed: none" alone is insufficient.

Matching numeric tokens is not enough: a preserved number can acquire the
wrong metric, unit or denominator. Deterministic checks cover declared literals
and references; numerical interpretation remains an evidence-grounded check.

## 6. Stop, reopen or escalate

Before a patch, name the defect and what would demonstrate its resolution.
Afterward, check that condition and protected meaning. Permit pass/no change.
Repeated failure triggers a question about evidence, warrant, reader path or
concept, not a command to "polish again". Do not impose a universal revision
count, metadiscourse quota or preferred vocabulary distribution.

Convergence is the author's accepted, adequately supported local argument with
understood scope and no unresolved material blocker. New evidence may reopen
it. Preserve the reason and affected dependencies; do not penalize a justified
pivot as instability. Optional style dissatisfaction can remain non-blocking.

Validate the protocol with [paired positive/negative cases](../evaluation/w0-language-and-convergence-cases.md).
