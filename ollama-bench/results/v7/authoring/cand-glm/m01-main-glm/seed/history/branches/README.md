# Branch workflow

Every branch under this directory proposes a new value for one stage's `dwell_s`
configuration row - the module's `EFFECTIVE_DWELL_S` constant is the number
actually honoured. Once a stage enters this workflow this project calls that
number the stage's **dwell**.

A branch's own record states only its own outcome: whether it merged, whether it
was withdrawn before merging, and, if it reverts an earlier branch, which one. A
merged branch does not by itself say whether the document was ever brought in line
with it - read the document too. A stage can carry more than one branch record;
read every one filed for a stage, not only the one opened first, before deciding
what its dwell currently is.

## Onboarding

A stage is tracked by this workflow from the date below. What that date is used for
is not this file's concern.

| stage | onboarded |
| --- | --- |
| `audit` | 2034-03-09 |
| `checkpoint` | 2034-05-05 |
| `compaction` | 2034-02-15 |
| `digest` | 2034-02-10 |
| `envelope` | 2034-05-09 |
| `ledger` | 2034-03-13 |
| `replay` | 2034-04-10 |
| `retention` | 2034-04-23 |
| `rollup` | 2034-03-05 |
| `shard` | 2034-04-13 |
| `throttle` | 2034-04-20 |

## Stages with no branch record

Any stage not listed above has never entered this workflow; its documented dwell
has never been proposed against and still equals the module's `EFFECTIVE_DWELL_S`.
