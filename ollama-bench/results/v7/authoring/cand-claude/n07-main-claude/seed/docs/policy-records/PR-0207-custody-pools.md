# PR-0207 - custody pools: which source is authoritative, and how a document is
corrected

- Status: **in force**
- Supersedes: PR-0161 (custody is a per-stage setting)
- Applies to: every stage named in `config/manifest.json`

## The ruling

The modules are what happens. A component document is what an operator was told. When
a component document's `custody_days` disagrees with the period the platform is
enforcing for that stage, the document is a documentation defect and is reported as
one. The module is never edited to match the document.

This record rules on **authority and procedure**. It does not say how a stage's
period is worked out, which stages are affected, or what a pool is; those are matters
of definition and they live in `docs/custody-policy.md`, because a definition with
two copies is a definition with two meanings.

## Who may change a component document

The stage's owner, named at the top of the document, and nobody else. A reviewer may
not, and a reviewer who does has destroyed the evidence that the defect existed. This
is the same rule as the incident-evidence rule and it is there for the same reason:
a review that repairs what it measures has measured nothing.

## How a reviewer files a correction instead

As rows in `data/doc-corrections.csv`, one per stale document, three fields:

    <stage>,<the stage that roots its custody pool>,<the period it should state>

The file is the reviewer's, is written fresh each review, and is not a repository
artifact: it is deleted once the owners have applied it.

## What the checker does, and what it deliberately does not do

`python3 tools/run_checks.py` validates a filed correction set. It checks that each
row names a real stage, that the pool named really does root a pool, that the period
is that pool's, and that the row is a correction at all rather than a restatement of
what the document already says. It then compares the fingerprint of the whole set
with the fingerprint the last review recorded in `data/custody-review.lock`.

It does **not** tell a reviewer which documents are stale. That was raised at the
time and was refused: a checker that answers the question it is asked to verify is
verifying itself, and the 2034 audit that worked that way passed a correction set
that had been copied out of the checker's own output and was wrong in the same way
the checker was. The fingerprint is recorded instead of the list for the same reason,
so that each review re-derives the list from the platform rather than carrying the
last one forward.

## What is not a finding

- A `REQUESTED_CUSTODY_DAYS` that disagrees with a document. That constant is a
  record of what was asked for at onboarding and is read by nothing. See
  `docs/custody-policy.md`.
- A history entry quoting an old period. History is dated and is evidence; a
  superseded entry least of all is a live instruction.
- A spot check. A partial sweep is not a review and is not accepted as one; the
  phrase for one is a spot check and it is written down as one so that nobody files
  it as this.
- Anything outside the manifest's stage list. A finding against something that is not
  a stage has no owner to send it to.

## Reporting

A review names the stages, states whether the checker accepted the correction set,
and cites the fingerprint of the schedule it applied so that the review can be
re-run against the same schedule later. It does not carry the periods themselves: a
report that carries the numbers gets quoted after the numbers have moved.

## History

PR-0161 made custody a per-stage setting and did not survive the first cross-stage
lineage question, which needed four stages to have kept evidence for the same length
of time and found that three of them had not. PR-0184 proposed a table of pool
membership under `config/` and was withdrawn within a fortnight, because the merge
moved stages twice while it was being written. This record is the third attempt and
is the first that has survived a quarter.
