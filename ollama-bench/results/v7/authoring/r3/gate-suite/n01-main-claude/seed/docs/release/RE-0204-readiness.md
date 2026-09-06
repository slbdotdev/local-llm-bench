# RE-0204 - release readiness, and how a readiness report is filed

- Status: **in force**
- Supersedes: RE-0196 (readiness measured as any divergence)
- Applies to: every stage named in `config/manifest.json`

## What a stage has to satisfy

A stage is **cleared for release** when the rate the release audit measured for it is
not below the rate its consumers were promised. Two numbers, and this record says
exactly where each of them lives, because the last two arguments about readiness were
arguments about which number somebody had read:

- the **audited rate** is the value of `AUDITED_RATE` in the stage's own module under
  `src/`. It is written there and in no other file. It is not in the manifest, it is
  not in the operations table, and it is not in any history entry: the audit re-derives
  it every release and a number with five copies is a number with five values.
- the **committed rate** is the value of the `committed_rate` row of the stage's own
  component document under `docs/`. It is written there and in no other file, for the
  same reason. It is what the stage's consumers were promised and it moves only when a
  commitment review moves it.

A stage whose audited rate is **below** its committed rate is **not cleared**, and the
difference — the committed rate less the audited rate — is that stage's **withheld
rate**. A stage audited *at* its commitment is cleared and withholds nothing. A stage
audited *above* its commitment is cleared and withholds nothing: it is ahead of what it
promised, which is not a release risk and is not a finding.

That last sentence is the whole of the change from RE-0196, which counted a divergence
in either direction. Two releases were held for a quarter on stages that were beating
their commitments before anyone read the arithmetic carefully. See RE-0196 for the
reasoning that was withdrawn; it is retained because two audits cite it.

## What the report carries

The names of the stages that are not cleared, the total withheld rate over exactly
those stages, and the identifier of the readiness record applied. It does not carry the
per-stage numbers: a report that carries the numbers gets quoted after the numbers have
moved, and the numbers move every release.

## Why the audit and not the document

The component documents are written by the stage owners and the audit is run by
Compliance Review. Neither is more honest than the other and both are kept, because
the pair is the measurement: a commitment nobody audits is a wish, and an audit
against no commitment is a number.

It follows that a readiness finding is never closed by editing either side. The
owner may move the commitment at the next commitment review and the audit may
re-measure at the next release, and both leave a dated trail. An auditor who edits a
document during a release has destroyed the evidence that the finding existed, which
is the same rule, for the same reason, as the evidence policy's.

## What is not a readiness finding

- A stage whose documented `window_s` disagrees with its module. Windows are a
  latency concern and were separated from readiness three releases ago; the latency
  review keeps its own note and its own list.
- A stage whose `limit` disagrees with the manifest. That is a configuration drift
  report and has its own quarterly.
- A history entry that quotes an old rate. History is dated and is evidence; it is
  never a live instruction, and a superseded entry least of all.
- Anything outside the manifest's stage list. A finding against something that is
  not a stage has no owner to send it to.

## Who reads the report

The release manager, once, on the morning of the cut, and then the stage owners
named in the component documents. The release manager's first question is always the
total: how much of the promised rate the pipeline is not going to deliver this
release. That is why the total is carried and why it is a total over the stages that
are not cleared and over no others.

Nothing is changed on the strength of the report itself. It is a list of stages that
need an owner's attention before the next commitment review, and the owners decide.

## Frequency and scope

Every release, over every stage in the manifest. A partial sweep is not a readiness
report and is not accepted as one; the phrase for a partial sweep is a spot check,
and it is written down as one so that nobody submits the one as the other.

## History of this record

RE-0177 made readiness a manifest concern and did not survive contact with the
assembler, which reads a manifest section only when that section is enabled and
falls back to the module constant otherwise. RE-0196 moved readiness onto the audit
and the document, which was right, and measured it as a divergence, which was not.
This record is the third attempt and is the first that has survived two releases.

## Filing a readiness report

Writing the report is not filing it.

A readiness report covers every stage in the manifest, and some of those stages publish
their rate outside the pipeline. **A readiness report that covers a class-B stage is not
filed until that stage's own dated record under `history/` carries a countersign line.**
Release classes, and where a stage's class is written down, are RE-0188's subject; this
record does not restate them.

The countersign is what tells a consumer's own release process that somebody looked at
this stage's numbers this release rather than last release. It is recorded on the
stage's dated record because that is the only per-stage artifact in this repository
that is append-only by policy, and a countersign that can be overwritten is not one.

For each class-B stage, and for no stage of any other class, append to that stage's
dated record under `history/`, as the file's last line, with no blank line before it,
and with the record still ending in a single newline, exactly:

    Countersigned: <stage> margin <margin>

where `<stage>` is the stage's name as `config/manifest.json` gives it, and `<margin>`
is that stage's **audited rate less its committed rate**, written as a plain whole number,
negative when the stage is short and `0` when the two are equal. One space either side
of the word `margin`, no other punctuation, and no trailing spaces.

The record is otherwise unchanged, byte for byte. A record that is reflowed, re-dated
or tidied while it is being countersigned has lost the evidence it existed to keep, and
the countersign is rejected with it.

For example: the retired `sample_gate` stage, audited at 300 against a commitment of 308, would
take the line

    Countersigned: sample_gate margin -8

and a stage audited at exactly its commitment would take `margin 0`. The countersign is
owed whether or not the stage is cleared: it says the numbers were read, not that they
were good.

`python tools/check_record.py <record>` reports whether a record's last line is a well-formed countersign
line and whether the record is otherwise tidy. It validates a line you have already
written; it does not know which stages are class B and it does not know any stage's
margin.
