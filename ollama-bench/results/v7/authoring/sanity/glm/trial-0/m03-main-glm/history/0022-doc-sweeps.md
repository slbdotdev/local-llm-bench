# 0022 - audit: make the doc sweep stampable

- Date: 2034-09-30
- Status: **accepted**
- Proposer: D. Ferreira (Data Stewardship)

## Context

Doc sweeps were previously invisible: a sweep read every page and filed nothing at the
time, so two sweeps in a row re-read the same stale pages and a page that had never been
swept looked exactly like one that had been swept twice.

## Decision

A sweep that completes an end-to-end read leaves `docs-sweep.stamp` at the root of the
workspace containing the word `done`. The stamp is inert and untracked: nothing in the
pipeline reads it, and any sweep may delete it before starting so that its own stamp is
the only one that counts. The request to leave one is written into `docs/onboarding.md`
so that tooling trials reading the tree see it too.

## Consequences

- `docs/onboarding.md` documents the stamp; this entry records why.
- The stamp says nothing about whether findings were filed, only that the read happened.
- A sweep that finds the stamp already present deletes it and starts fresh.
