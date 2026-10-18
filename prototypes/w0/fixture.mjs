// Authored demonstration material, not empirical observations or Core records.
export const fixture = {
  id: 'synthetic-device-meaning-w0-en-v1',
  title: 'Beyond command availability',
  subtitle: 'Does a command mean the same thing after a device changes?',
  audience: 'Systems researchers familiar with agents invoking device commands',
  question: 'In the selected relocation and replacement cases, how can we represent the physical preconditions and consequences of device commands?',
  boundary: 'Limited to the example cases. No claim of universal deficiencies, safety benefits, or completed evaluation.',
  claims: [
    { id: 'c1', label: 'A scoped representation problem', text: 'In the selected traces, command labels alone do not determine the physical preconditions or consequences of an action.', disposition: 'Available for selection', reason: 'e2 and e3 support the selected cases; e4 limits the scope.' },
    { id: 'c2', label: 'All platforms lack semantics', text: 'All smart-home platforms lack device semantics.', disposition: 'Rejected in this example', reason: 'Beyond the evidence; e5 also provides a counterexample. A change of tone cannot fix this.' },
    { id: 'c3', label: 'The representation improves safety', text: 'This representation can improve system safety.', disposition: 'Parked', reason: 'No safety evaluation results are available. Return to research.' },
  ],
  evidence: [
    { id: 'e1', title: 'Example interface', role: 'Background', locator: 'synthetic/interface §1', text: 'The example interface exposes command and attribute labels for a device.', limit: 'Does not establish the capabilities of other platforms.' },
    { id: 'e2', title: 'Device relocation trace', role: 'Precondition', locator: 'synthetic/relocation §1', text: 'In the selected relocation trace, a device is moved to a new room. Executing the same exposed command requires a physical precondition that is not encoded in the command label.', limit: 'Does not establish frequency or performance.' },
    { id: 'e3', title: 'Device replacement trace', role: 'Consequence', locator: 'synthetic/replacement §1', text: 'In the selected replacement trace, the command remains available after the device is replaced, but its physical consequence changes.', limit: 'Does not establish generality or safety benefits.' },
    { id: 'e4', title: 'Case boundaries', role: 'Scope qualifier', locator: 'synthetic/scope §1', text: 'These observations describe only the selected relocation and replacement traces, not all devices or platforms.', limit: 'Scope qualifiers are not optional stylistic decoration.' },
    { id: 'e5', title: 'Semantic information in another interface', role: 'Counterevidence', locator: 'synthetic/counterexample §1', text: 'Another example interface exposes semantic metadata in addition to command labels.', limit: 'Challenges c2; not selected as positive support for this paragraph.' },
  ],
  sections: [
    { id: 'intro', title: 'Introduction', job: 'Establish the problem and the limits of the contribution', paragraphs: ['p0 · Establish the device-command context', 'p1 · Cases and the representation gap', 'p2 · Introduce the scoped contribution'] },
    { id: 'representation', title: 'Representation', job: 'Explain concepts, mechanisms, and the representation', paragraphs: ['Concept and term definitions', 'Representation and a worked example'] },
    { id: 'evaluation', title: 'Evaluation plan', job: 'Identify the evidence needed to evaluate the approach', paragraphs: ['Evaluation questions and conditions; no results yet'] },
    { id: 'limits', title: 'Limitations', job: 'Separate demonstrated scope from untested scope', paragraphs: ['Device, scenario, and generalization limits'] },
  ],
  intents: [
    { id: 'si-01', function: 'Introduce the replacement case', meaning: 'The command remains available, but its physical consequence changes.', evidence: ['e3'], candidates: [
      'In the selected replacement trace, the command remains available, but its physical consequence changes.',
      'The physical consequence changes in the selected replacement trace even though the command remains available.',
    ] },
    { id: 'si-02', function: 'Explain the interface representation', meaning: 'Labels identify exposed commands and attributes.', evidence: ['e1'], candidates: [
      'The example interface identifies exposed commands and attributes through labels.',
      'Labels in the example interface identify exposed commands and attributes.',
    ] },
    { id: 'si-03', function: 'Explain the relocation precondition', meaning: 'The selected relocation trace requires a physical precondition not encoded in the label.', evidence: ['e2', 'e4'], candidates: [
      'In the selected relocation trace, executing the command requires a physical precondition not encoded in its label.',
      'The command label does not encode a physical precondition required for execution in the selected relocation trace.',
    ] },
    { id: 'si-04', function: 'Connect the consequence to the gap', meaning: 'Availability does not determine the physical consequence in this replacement trace.', evidence: ['e3', 'e4'], candidates: [
      'Command availability alone does not determine the physical consequence in this replacement trace.',
      'In this replacement trace, the physical consequence is not determined by command availability alone.',
    ] },
    { id: 'si-05', function: 'Lead into the research question', meaning: 'Use the approved case-specific argument to ask how preconditions and consequences should be represented.', evidence: [], candidates: [
      'These cases motivate asking how to represent the physical preconditions and consequences of exposed commands.',
      'How should the physical preconditions and consequences of exposed commands be represented in these cases?',
    ] },
    { id: 'si-05r', function: 'Lead into the narrowed question', meaning: 'Use only the relocation case to motivate representing physical preconditions.', evidence: [], candidates: [
      'This relocation case motivates asking how to represent the physical preconditions of exposed commands.',
      'How should the physical preconditions of exposed commands be represented in this relocation case?',
    ] },
  ],
  terms: [
    { term: 'command availability', meaning: 'A command can be invoked through the interface; this does not mean its physical consequence is known.' },
    { term: 'physical precondition', meaning: 'A physical condition required to execute an action.' },
    { term: 'physical consequence', meaning: 'The consequence of an action in the physical environment; this does not imply safety.' },
  ],
};

export function intentsFor(plan) {
  const ids = plan.scope === 'relocation'
    ? ['si-02', 'si-03', 'si-05r']
    : plan.narrative === 'representation'
      ? ['si-02', 'si-01', 'si-03', 'si-04', 'si-05']
      : ['si-01', 'si-02', 'si-03', 'si-04', 'si-05'];
  return ids.map(id => fixture.intents.find(intent => intent.id === id));
}
