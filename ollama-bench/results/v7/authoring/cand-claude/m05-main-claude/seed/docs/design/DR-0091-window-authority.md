# DR-0091 - window authority

- Status: **in force**
- Supersedes: DR-0055 (the document was authoritative)

## The rule

Every stage's component document carries a documented enforced-window setting in its
configuration table. Where that number disagrees with the module's `ACTIVE_WINDOW_S`, the **module
governs**: the document is what an operator was told and the module is what the
code does, and a checklist against this record corrects the document's row to the
module's number. The module is never changed to match a document.

## What changed

DR-0055 asked an operator to keep a component document's enforced-window row in step
with the module by hand, on the theory that a document a person maintains is less
likely to drift than a constant nobody looks at twice. It drifted anyway: three
incidents in one quarter traced back to a document that said one number while the
code enforced another, and in every case the document was the one that had not been
touched.

## Why the module and not the document

The module is what runs. A document is a claim about what runs, and a claim is only
as good as the last time someone remembered to update it. Making the module
authoritative does not make documents unnecessary; it makes a disagreement between
them a documentation defect with a known fix, rather than an open question about
which one the on-call engineer should trust at 3 a.m.

## What this does not cover

A stage exempted from this comparison by a current migration note is not covered by
this ruling either way: its document is not wrong, it is describing a number this
record does not apply to yet. See the migration note for which stages that is and
why.
