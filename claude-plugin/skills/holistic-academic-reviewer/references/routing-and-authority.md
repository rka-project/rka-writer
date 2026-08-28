# Routing and Authority

Classify the primary artifact before reading it deeply. Use filenames, document structure, surrounding files, and the requested outcome. Ask one artifact-type question only when the route remains genuinely ambiguous.

## Route map

| Artifact and requested outcome | Native engine | Native modes |
|---|---|---|
| Research paper, journal or conference manuscript, publication revision, peer-review or rebuttal simulation | sibling `ai-cyber-paper-reviewer/` | `quick`, `standard`, `full-forensic`, `interactive`, `re-review`, `focused` |
| Proposer-owned NSF CISE proposal or section, CAREER package, mock panel, proposal revision | sibling `nsf-cise-mock-panelist/` | `full-panel`, `single-review`, `section-review`, `editorial-audit`, `revision-check` |

If an artifact fits neither route, do not force it into an unrelated engine. State the coverage limit and request a more appropriate review workflow.

Resolve `<skill-dir>` to the directory containing the router `SKILL.md`, set `<skills-dir> = <skill-dir>/..`, then set `<paper-engine-dir> = <skills-dir>/ai-cyber-paper-reviewer` and `<proposal-engine-dir> = <skills-dir>/nsf-cise-mock-panelist`. Read the chosen engine's `SKILL.md` completely. Resolve every selected engine-relative reference, schema, script, asset, and command path against that engine directory, never against the router skill.

Do not reinterpret native contracts:

- The paper engine owns `schemas/review-bundle.schema.json`, its model-family registry, decision scale, interactive protocol, and assurance values `single_pass_advisory`, `provisional_advisory`, `cross_model_advisory`, and `human_panel`.
- The proposal engine owns its individual-review and panel-summary schemas. Its JSON rating bands are `excellent`, `very_good`, `good`, `fair`, `poor`, and `unrated`; its mock dispositions are `highly_competitive`, `competitive`, `borderline`, `not_competitive`, `no_consensus`, and `unrated`; its assurance labels are `provisional_advisory`, `multi_family_advisory`, and `human_calibrated_advisory`.
- Do not translate, average, normalize, or compare these values numerically across engines. Do not claim a validator mode, rating, or assurance label unless the native engine produced and validated it.

Keep proposal `section-review`, `editorial-audit`, and `revision-check` scoped when no complete holistic review was performed. Do not fabricate proposal-wide Intellectual Merit, Broader Impacts, dimensions, or ratings merely to populate a native holistic schema.

## Mixed packets

When both a paper and proposal are review targets, create independent input manifests and run both engines separately. Do not expose one engine's verdict to the other's sealed reviewers. Keep native findings and scores in distinct route directories. A root session index may link related claims, but it must not produce a combined score, recommendation, acceptance/funding probability, or assurance claim.

Supporting papers inside a proposal packet are evidence unless the user also requests paper review. A solicitation, style guide, prior review, bibliography, or response letter is supporting material, not a second primary route.

## Authority order

For papers, establish the exact venue, year, track, paper type, and review stage when they affect policy or scoring. Use current official venue sources for desk rules; separate policy from scientific judgment.

For NSF proposals, use the exact solicitation and track, current NSF policy, official program guidance, and institutional guidance in their proper authority order. Record URLs, sections, effective and access dates, applicability, overrides, and open conflicts. Never treat generic grant advice or an author guide as controlling authority.

## NSF official-review hard stop

Before opening likely NSF proposal content, establish provenance. If the material came through service as an actual NSF reviewer, panelist, or staff member, stop without ingesting, copying, summarizing, or uploading it. A statement that the work is “internal” does not waive NSF confidentiality or approved-tool restrictions. Continue only with proposer-owned drafts, institution-authorized materials, public examples, or other material explicitly authorized for internal mock review.

Keep proposal transfer authorization separate from external novelty-query authorization. When confidential query terms could reveal unpublished ideas, obtain permission and use approved sanitized queries.

## Root privacy summary

Treat the session envelope's `privacy_mode` as a compact summary, never as permission that weakens a native engine's more specific rules:

- `local_only`: make no additional outbound disclosure beyond the chat or runtime the user already authorized by supplying the material. In a web chat, this does not mean processing occurs only on the user's computer.
- `metadata_only_external_verification`: limit external checks to citation metadata, titles, DOI or venue pages, standards identifiers, official policy, and short non-unique queries that do not reveal unpublished content.
- `author_authorized_full_external_check`: use only after the user authorizes the exact provider and content class to be transferred.

For NSF material, also preserve the proposal engine's separate proposal classification, literature-query authorization, and full-artifact transfer authorization. Apply the stricter recorded boundary whenever the root summary and native record differ.
