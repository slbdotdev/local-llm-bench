# RE-0188 - release classes

- Status: **in force**
- Applies to: every stage named in `config/manifest.json`

A stage's **release class** says who is exposed when the stage is late, and it is the only
stage property in this repository that is a human judgement rather than a measurement.

## The classes

- **A - interior.** The stage's output is consumed inside this pipeline and nowhere else.
  Its rate is a matter between it and the stages either side of it. Most stages are class A.
- **B - boundary.** The stage publishes its rate to a consumer outside this pipeline, under
  an agreement that consumer's own release process depends on. A class-B stage is the only
  kind whose numbers leave the building, and the release process treats it differently for
  that reason and for no other.
- **C - terminal.** The stage is the last thing on its own shutdown path and publishes nothing
  at all. A class-C stage may be late without anybody outside noticing, which is why it is
  kept apart from class A rather than folded into it.

## Where a class is written down

**A stage's release class is the value of `RELEASE_CLASS` in the stage's own module under
`src/`, and it is written in no other file.**

That is deliberate and it is worth the inconvenience. The manifest is regenerated from the
assembler on every deploy, so anything the assembler cannot derive would be silently dropped
from it, and a release class is exactly the kind of thing the assembler cannot derive. The
operations table is generated from the manifest and inherits the same defect. So the class
lives beside the code it describes, where a change to it is a code review.

Two things it is not, both of which have been read as it at least once:

- the manifest's `class` field, which is the name of the Python class the module defines. It
  is a class in the programming sense and has nothing to do with a release class.
- the on-call team in `docs/operations.md`. A team owns a stage; it does not classify it.

## Changing a class

A class change is a code change with two reviewers, one of whom is from Compliance Review.
There is no expedited route and there has never been an emergency reclassification, because a
reclassification changes what this repository owes to somebody outside it.
