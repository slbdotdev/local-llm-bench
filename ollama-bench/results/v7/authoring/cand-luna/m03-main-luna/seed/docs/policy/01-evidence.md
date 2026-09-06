# Policy: evidence

*What counts as evidence, and why a snapshot's timing matters.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every
component document and every history entry on its own subject.** It says
nothing about capacity exceptions and does not narrow, grant or forbid anything
on that subject; a reader looking for this quarter's exemption ruling will not
find it here.

## Rules

1. A record that has reached `settled` is immutable. No stage, no operator and
   no repair script may alter it.
2. An `abandoned` record is retained for the full retention term of its class,
   even when it is obviously the result of a defect.
3. The retention term is a property of the record's class and never of the stage
   that produced it.
