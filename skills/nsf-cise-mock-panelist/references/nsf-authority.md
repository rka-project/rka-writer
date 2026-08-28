# NSF authority and panel structure

This is a routing guide, not cached submission authority. Refresh live sources for every proposal.

## Authority order

1. Exact solicitation, amendments, incorporated FAQs, and program-specific reviewer instructions.
2. Applicable NSF policy notices and the current PAPPG, including supplements.
3. Current Research.gov Proposal Evaluation System and proposal-preparation instructions.
4. Current CISE directorate/division/program guidance.
5. Institutional requirements, when reviewing submission readiness.
6. This skill's internal rubric.

Record URL, title, section, effective date, access date, applicability, and any higher-authority override. If sources conflict or cannot be verified, label the point `open question`; do not silently choose a convenient rule.

## Current general merit-review core

Verified 2026-07-20; refresh before use.

- NSF uses Intellectual Merit and Broader Impacts. Program solicitations may add criteria: https://www.nsf.gov/funding/merit-review
- The current base guide is PAPPG 24-1, with later supplements listed on the live landing page: https://www.nsf.gov/policies/pappg
- Supplement 1 (NSF 26-200), effective 2025-12-08, modifies proposal-processing and review provisions. Unless excepted, a full proposal must receive at least two reviews, one of which may be conducted internally by NSF staff: https://www.nsf.gov/policies/document/pappg24-1-supplement-1
- Supplement 2 (NSF 26-202), effective 2026-01-22, changes Data Management and Sharing Plan handling and makes the plan part of merit review: https://www.nsf.gov/policies/document/pappg24-1-supplement-2
- PAPPG Chapter III describes the general review process and reviewer-selection principles: https://www.nsf.gov/policies/pappg/24-1/ch-3-proposal-processing-review
- PES panelist FAQ: https://www.nsf.gov/policies/document/faq-proposal-evaluation-system-pes-panelists
- Reviewer orientation and bias/constructiveness guidance: https://www.nsf.gov/od/oia/merit-review-orientation
- Panelist confidentiality and conflict information: https://www.nsf.gov/about/meetings/panelists
- NSF conflict-of-interest policy: https://www.nsf.gov/policies/conflict-of-interest
- NSF's notice on generative AI in merit review: https://www.nsf.gov/policies/ai/merit-review
- CISE directorate: https://www.nsf.gov/cise
- NSF Award Search: https://www.nsf.gov/awardsearch/

For both Intellectual Merit and Broader Impacts, the general NSF elements ask about:

1. potential to advance knowledge or benefit society;
2. creative, original, or potentially transformative concepts;
3. a well-reasoned, well-organized plan with a mechanism to assess success;
4. qualifications of the individual, team, or organization;
5. adequacy of available resources.

Treat these as the general floor. Add exact solicitation criteria without rewriting or collapsing them.

The skill's three-reviewer panel is an internal reliability design, not a claim that NSF always assigns exactly three reviews. Use the exact opportunity and panel instructions for the applicable process.

## Generative-AI hard stop for official review material

NSF's current merit-review AI notice prohibits reviewers from uploading proposals, review information, panel summaries, or recommendations to non-approved generative-AI systems. Therefore:

1. ask how the material was obtained before opening it;
2. if it came through official NSF reviewer, panelist, or staff service, stop without ingesting its contents;
3. do not treat the user's statement that use is “internal” as a waiver of NSF confidentiality or approved-tool rules;
4. restrict this skill to proposer-owned drafts, public examples, or materials for which the organization has authority to run an internal mock review.

If provenance is ambiguous, pause and resolve it. This boundary applies before any proposal text is sent to an agent or external search service.

## Mimic the public PES structure, not NSF authority

Public PES guidance says individual panel reviews include:

- one or two rating selections;
- Intellectual Merit strengths and weaknesses;
- Broader Impacts strengths and weaknesses;
- additional solicitation-specific criteria when configured;
- an overall summary statement.

It also distinguishes individual reviews from a later panel summary, with lead, scribe, and collaborative agreement roles when that workflow applies. Public PES guidance notes that some panels prepare panel summaries without individual reviews. This skill deliberately uses sealed individual reviews followed by synthesis as an internal reliability default, not as a universal statement about NSF panel procedure. The mock panel must not represent itself as PES, NSF staff, or an official panel.

The public rating words may be mirrored only as a disclosed mock scale. Do not map the internal `mock_disposition` to an award recommendation, funding chance, or portfolio decision.

## Why solicitation extraction must be live

CISE opportunities differ. For example, the Future CoRe solicitation (NSF 25-543) and Secure and Trustworthy Cyberspace 2.0 solicitation (NSF 25-515) do not expose identical program-specific review instructions:

- https://www.nsf.gov/funding/opportunities/future-core-computer-information-science-engineering-future-computing/nsf25-543/solicitation
- https://www.nsf.gov/funding/opportunities/satc-20-security-privacy-trust-cyberspace/nsf25-515/solicitation

These are examples, not defaults. For each proposal, extract the actual opportunity's criteria, track rules, special sections, and return-without-review conditions into `authority-snapshot.md` with a verification date.

## Separate compliance from merit

Run a preliminary compliance screen because NSF may return a nonconforming proposal without review. Do not lower a merit rating to encode a formatting or eligibility problem. Report:

- `verified requirement` with authoritative citation;
- `applies` with reason;
- `status` as pass/fail/TBD;
- `severity` and owner;
- evidence path and verification date.

If the exact solicitation is absent, the mock panel may provide a provisional merit critique but may not give solicitation-fit, compliance, or submission-readiness conclusions.

## Conflict, confidentiality, and identity

Before reviewing, record whether the reviewer has a personal, institutional, collaborative, financial, advisory, or competitive conflict. In an AI simulation, also reduce identity cues when they are not needed for evaluating team qualifications. Never infer team quality from institutional prestige.

Keep unpublished proposals and review traces local. External novelty searching may reveal a research direction; obtain authorization and use sanitized claim queries when appropriate.
