# Worker boundary cases

Worker aliases are `jobs` and `batch`. Their targets are not recursively
looked up, and source case is not folded. A source called `Jobs` is unknown.
The source-specific key table belongs to canonical worker and maps `job` and
`task` to jobs. The global table runs first for all other worker keys.

A worker record may begin with a void task, then add job, then hold task. The
void is not an occurrence and does not reserve jobs. The add creates jobs; the
hold updates it with zero contribution and increments count. If its labels are
new after canonicalization, they append in order.

Worker queues can report negative values. A remove of -2 adds two to total; an
adjust of -2 subtracts two; an add of -2 also subtracts two. The action, not
the sign, selects the arithmetic. Counts remain positive observation counts and
are never inferred from a total.

An empty batch page with source batch creates worker when it is the first page.
When worker already exists it changes nothing. A rejected-only page shares that
lifecycle behavior. This is important in the queue UI, which distinguishes
“worker reported but no accepted observations” from “worker absent.”

The result has only public source, entries, key, total, occurrences, and labels
fields. Queue implementation values such as raw action, page, multiplier, or
position map are not emitted.
