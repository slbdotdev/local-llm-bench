# Policy: guarantees

*What a stage guarantees to repair traffic, when a guarantee stops and starts applying, and
which disagreements between a document and the pipeline are reported at all.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component document
and every history entry.** Where a component document describes behaviour this policy forbids,
the component document is stale and is to be corrected, not followed.

## Bands

A stage guarantees part of every drain to repair traffic. The guarantee is split into
**bands**, one band per class of repair work, and each band has a **size**: the number of
records the stage guarantees that class out of every drain.

A stage's bands and their sizes are **commissioned in the stage's module and recorded nowhere
else**. A size copied into a document is stale the day the module changes, and this project
has been bitten by a number with five copies once already; so the documents describe the bands
and never repeat their sizes.

## Which bands a stage holds

A stage does not necessarily hold every band it was commissioned with. Bands are stood down
and taken back up by dated decision, and the decisions for a stage are recorded in that
stage's own entry under `history/`. Those entries are written by whoever proposed the change
and the wording varies:

- a band is **no longer held** from an entry that records it *retired*, *stood down*, *handed
  back* or *withdrawn*;
- a band is **held again** from a later entry that records it *reinstated*, *restored* or
  *taken back up*.

The entries for a stage are applied in the order they are recorded, oldest first. A stage that
has no such entry holds every band its module commissions.

Every history entry ends with a line saying that the stage's component document states the
current behaviour and is authoritative over that entry. That line is about the entry's own
ruling on `limit`, which the component document restates in its configuration table. It is not
about the band record, and it does not survive this policy in any case: a component document
is a description of the pipeline and never a source for it.

## The held allowance

A stage's **held allowance** is the sum of the sizes of the bands it holds. It is written down
nowhere, and deliberately: it is what a module and a decision entry say together, so it is
recomputed at every assembly rather than quoted. A number quoted from a document is evidence
of nothing.

## Decisions in this area

### DR-0098 - 2033-11-02 - superseded

*A band stood down keeps its guarantee until the stage is next commissioned.* The assembler
was held to read the module and nothing else, so a decision entry described an intention and
the module described the behaviour; a stage's held allowance was therefore the whole allowance
its module commissioned, whatever its entries recorded.

**Superseded by DR-0143.** It is kept because two audits cite its reasoning, and a superseded
decision is evidence rather than a live instruction.

### DR-0143 - 2034-02-16 - in force

The assembler re-reads a stage's decision entries at every assembly, so a stand-down takes
effect at the next drain and not at the next commissioning. Accordingly:

1. The bands a stage **holds** are the bands its module commissions, less those its own entry
   has stood down and not since taken back up, applied oldest first as above.
2. A component document's **Bands held** line is a claim about the pipeline. Where it names a
   different set of bands than the stage actually holds, the document is a **documentation
   defect**. The document is reported; it is not repaired during an audit, and no module is
   ever changed to make a document true.
3. A component document whose header carries a **provisional** status is a draft. It does not
   yet claim to describe the assembled pipeline, so a disagreement with it is not a defect and
   is not reported. It is named separately instead, so that the rewrite queue can be checked
   against the audit.
4. A defect is reported by naming the stage. A report does not carry the band sets or the
   sizes: a report that carries the numbers is quoted after the numbers have moved.

## What this policy does not cover

It does not say what happens when a stage is at its `limit` and its held allowance exceeds the
work offered. That is a capacity question and it is answered in `docs/operations.md`, because
the answer depends on the stage and on how far the drain has progressed.
