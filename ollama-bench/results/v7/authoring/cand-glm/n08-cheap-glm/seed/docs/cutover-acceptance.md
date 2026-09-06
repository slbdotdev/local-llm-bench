# Cutover acceptance procedure

- Status: **in force**
- Applies to: every stage named in `config/manifest.json`
- Applied by: the cutover tooling, which reads the tree as it stands

## What on file means

The migration window opens only when every stage's acceptance is on file. A
stage's acceptance is **on file** when, and only when, the stage's module names
its acceptance record: the module carries an `ACCEPTANCE_RECORD` constant whose
value is the identifier of the record of acceptance for that stage. A module that
carries no such constant has no acceptance on file. This is a definition about
the tree as it stands and not about prose: the cutover tooling reads the modules,
never the documents, so a document that describes an acceptance the module does
not name describes an acceptance that is not on file.

## What signed means

An acceptance record is **signed** when the stage's component document carries
an `## Acceptance` section whose `countersigned:` line names a person. A section
whose `countersigned:` line does not name a person leaves the record on file but
**unsigned**. On file and unsigned is a different state from never filed: it is
chased with the owner, and it is reported separately. Neither state is the other,
and the cutover report asks for each of them by name.

## Batch acceptance

Stages accepted together at the pilot batch review name the batch record in the
same way. The batch record itself carries the countersignatures of its members,
and no component-document section is written for a batch member: its absence
from the component document is the sanctioned placement, not an omission. The
batch record is `docs/pilot-batch.md`, and its identifier is in its header. A
stage is on file and signed under the batch record when the record's member
table carries that stage's countersignature.

## The cutover report

The report names, in manifest order, the stages with no acceptance on file and
the stages whose acceptance is on file but unsigned. It states how many stages
are without a signed acceptance record on file, which is the two together, and
it cites the identifier of the record that covers the stages accepted at batch
level. The report is a read: nothing it examines is repaired while it is being
prepared, because a cutover that repairs what it measures has measured nothing.

