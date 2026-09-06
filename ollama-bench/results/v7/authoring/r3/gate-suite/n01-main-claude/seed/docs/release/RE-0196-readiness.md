# RE-0196 - release readiness (superseded)

- Status: **superseded by RE-0204**
- Supersedes: RE-0177 (readiness as a manifest concern)
- Applies to: every stage named in `config/manifest.json`

*Retained as evidence. Two audits cite the reasoning below and removing this record would
break those references. It is not a live instruction and it is not applied to a release.*

## The ruling that was withdrawn

A stage was **not cleared for release** when the figure the release audit measured for it
**differed** from the figure its consumers had been promised, in either direction. The report
named those stages, carried the total absolute difference over them, and cited this
record's identifier.

Where the two numbers live was settled by this record and has never been disputed since: the
measured figure is `AUDITED_RATE` in the stage's own module under `src/`, and the promised
figure is the `committed_rate` row of the stage's own component document under `docs/`.
Neither is in the manifest, in the operations table or in any history entry, because the audit
re-derives one of them every release and the commitment review moves the other, and a number
with five copies is a number with five values.

## Why the ruling was superseded

The symmetry was deliberate at the time. The argument for it was that a stage which beats what
it promised is as much a surprise to a capacity plan as one that misses it, because the stages
downstream of it size themselves on the promise rather than on the measurement.

That argument was wrong in practice and expensively so. Two releases were held for a quarter
over stages that were ahead of what they had promised, and in both cases the release manager's
own note says the report had been read as a list of problems, which is what a readiness report
is. A stage that is ahead of its promise is not a release risk; it is a promise that is due to
be revised at the next commitment review, and the commitment review has its own quarterly.

RE-0204 keeps everything above except the symmetry, and that is the whole of the difference
between the two records.
