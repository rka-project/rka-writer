# ADR 0005: Obtain inference only through an authenticated subscription host

- Status: Accepted
- Refined by: [ADR 0008](0008-paper-centered-incremental-commitment.md); authentication, included-only billing and actual isolation are independent gates. An auth probe alone is insufficient.
- Date: 2026-09-04
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1PKYTMA70XG0EVZPD7QSM2S`

## Context

A Writer-owned model gateway would require provider API credentials, separate
usage billing, secret storage, provider-specific model discovery, and fallback
policy. It would also make a model selector appear to be part of the research
workflow even though model choice does not authorize scientific meaning.

The intended product must use resources already included in the researcher's
Codex or Claude Code subscription. It must not require an API key or create an
unexpected API charge.

## Decision

RKA Writer delegates every model-assisted operation to an officially
authenticated subscription host. The initial host types are Codex and Claude
Code. Authentication, subscription entitlement, model availability, usage
limits, and model selection remain owned by the host.

Writer does not accept provider API keys, call provider model APIs, fund API
usage, expose a cross-provider model selector, or fall back to metered API
usage. Before dispatch, a host adapter must positively establish that the
current execution path uses subscription entitlement. Unknown, API-key,
metered, exhausted, or unsupported states fail closed.

Writer sends a bounded semantic task envelope and receives an untrusted
proposal. Deterministic admission, schema validation, dependency checks, and
researcher approval remain Writer responsibilities. Host credentials and
reusable authentication tokens never enter Writer state.

## Consequences

- Researchers can use Writer without separate API setup or API billing.
- The primary interface shows subscription-host status, not a model dropdown.
- Host-specific adapters remain thin; the Authoring Graph and admission rules
  stay provider-neutral.
- A model label is recorded as optional execution provenance only when the host
  exposes it.
- Host unavailability or exhausted subscription capacity stops model-assisted
  work instead of changing the billing path.
- Local-model, BYOK, direct-API, and Writer-funded SaaS execution are outside
  the baseline product.
- W0 must prove that an adapter can identify subscription-backed execution
  through a supported host interface without reading credential files.

## Alternatives rejected

### Bring your own API key

This violates the no-API product boundary and moves credential and billing
responsibility into Writer.

### Writer-funded API service

This introduces accounts, metering, abuse control, privacy policy, and hosted
research-data handling before the local authoring workflow is validated.

### Silent API fallback when a subscription is exhausted

This can create an unexpected charge and makes the runtime state impossible
for the researcher to reason about.

### Local models as an automatic fallback

This changes model capability and output behavior without researcher intent
and does not satisfy the subscription-only boundary.
