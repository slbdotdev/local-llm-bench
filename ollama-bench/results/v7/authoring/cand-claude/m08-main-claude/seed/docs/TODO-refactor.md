# TODO — unify the stage classes

*Filed after the third quarter in a row where a new stage needed the same eight
methods hand-written again. Nobody has picked it up; it is not blocking anything.*

Every stage class (`ThrottleGateway`, `SchemaGateway`, `AuditEngine`, and the rest) repeats the same shape: a limit, a
window, a dict keyed by an application-defined key, a seal flag, and four verbs that
differ only in which state string they write. A generic `Stage` base class,
parameterised by its verb list and its state names, would remove on the order of two
hundred near-identical lines and make the next new stage a manifest entry and a
twenty-line subclass instead of a full module.

## Why it has not happened

1. Every stage's tests assert on the concrete class name, so a mechanical rename
   would touch all nineteen test files as well as all nineteen modules — a bigger
   single change than anyone has been willing to review at once.
2. Two stages (`throttle` and `schema`) have a proposal on record to change their verb list
   independently of this refactor, and doing both at once would make either change
   hard to attribute if something broke. `throttle`'s proposal specifically touches the
   verb that emits its shed-count metric, which is exactly the kind of surface
   overlap that makes it easy to mistake `throttle` for whatever stage this quarter's
   open shed-count incident narrows to — the incident's own criterion, not this
   note, is what actually settles that.
3. Nobody has confirmed whether the generic base class approach would preserve the
   `snapshot()` sort-stability guarantee `docs/architecture.md` documents, which is
   exactly the kind of thing that is cheap to break silently in a generic rewrite.

## Scope, if someone does pick it up

One stage first, converted and left running beside the others for a full quarter,
before touching a second. Not all nineteen at once, and not as part of any other
change already in flight.
