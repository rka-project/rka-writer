# Permission Model

Permissions are defined by semantic effect rather than by the number of agents.

| Action | Model may propose | Researcher approval required | Automatic execution allowed |
|---|---:|---:|---:|
| Retrieve project-scoped Core context | Yes | No, within approved task scope | Yes |
| Select a paper question | Yes | Yes | No |
| Create or strengthen a publication claim | Yes | Yes | No |
| Interpret evidence use | Yes | Yes | No |
| Select a narrative move or paragraph contract | Yes | Yes | No |
| Lock or rename a technical term | Yes | Yes | No |
| Create a sentence intent | Yes | Yes | No |
| Realize an admitted sentence intent | Yes | Acceptance of realization | No |
| Apply a non-semantic formatting correction | Yes | Policy-dependent | Only when diff-bounded |
| Mark dependents stale after upstream change | No proposal needed | No | Yes |
| Rewrite stale prose | Yes | Yes | No |
| Write durable research meaning back to Core | Yes | Exact preview and confirmation | No |
| Import reviewer findings | Yes | Selection or triage authorization | No |

The initial runtime should use logical roles—Mentor, Realizer, Evidence Auditor,
and isolated Reviewer—only where their permissions differ. Agent count is not a
product feature.
