# W1 Acceptance Criteria

W1 validates one fully traceable paragraph, not general manuscript generation.

## Required fixture

The scenario contains:

- one provisional and one approved paper question;
- one publication claim with scope and strength;
- two to four evidence uses with exact Core or provisional-source bindings;
- two narrative alternatives and one researcher selection;
- one approved paragraph contract;
- four to six sentence intents;
- three to five term locks;
- accepted sentence realizations and one paragraph source map; and
- one later upstream claim revision.

## Functional gates

- Every realization passes sentence admission before generation.
- Each sentence traces to intent, paragraph contract, narrative move,
  publication claim, evidence use, term locks, and researcher authorization.
- Unselected evidence cannot enter the paragraph.
- A changed upstream claim marks exactly the affected artifacts stale.
- The upstream change produces no manuscript-byte mutation.
- The researcher can revalidate, revise, branch, or retire stale artifacts.
- Cold-start recovery reconstructs current accepted state and next decision.

## Hard safety gates

- Silent claim changes: 0.
- Silent term changes: 0.
- Silent evidence reinterpretations: 0.
- Silent upstream-triggered rewrites: 0.
- Unsupported factual or comparative statements: 0.
- Cross-project Core bindings: 0.

## Researcher-facing gates

- Consequential choices are understandable without exposing raw schemas.
- The researcher can explain why every sentence exists.
- No decision batch contains more than three genuinely coupled choices.
- The interface reveals impact before requesting regeneration.

Passing W1 authorizes W2 design; it does not by itself authorize a general
editor, section generator, or public Writer deployment.
