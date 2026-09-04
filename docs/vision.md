# Product Vision

## Problem

General-purpose writing agents can move from research records to polished prose
while silently choosing the paper's question, claim strength, evidence meaning,
narrative role, and terminology. Repeated broad rewrites can then oscillate
because upstream decisions are neither explicit nor versioned.

## Product thesis

RKA Writer progressively compiles reviewed research knowledge and explicit
researcher decisions into a versioned authoring graph. Prose is a downstream,
bounded realization of approved meaning rather than the primary state of the
system.

## Primary user

A researcher writing a technical paper who wants AI assistance without
delegating scientific meaning, evidence interpretation, or final terminology.

## Goals

- converge from central research questions to sentence-level realization;
- keep claims, evidence use, narrative function, and terms explicit;
- make every manuscript sentence traceable to an approved intent;
- expose the impact of upstream changes without automatic rewriting;
- resume work across sessions without asking the model to reconstruct intent;
- use RKA Core as the primary provenance substrate; and
- support local, privacy-preserving manuscript work.

## Non-goals

- one-click paper generation;
- autonomous selection of consequential scientific meaning;
- storing canonical research truth inside Writer;
- treating a model transcript as durable authoring state;
- automatic incorporation of reviewer findings;
- copying the entire RKA database into a model context; or
- building a general editor before the W1 convergence path is validated.
