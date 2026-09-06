# Pending migrations

*Follow-up migrations obliged by a fix already identified elsewhere, but not yet
made. Each row is independent; a stage not listed here has no pending migration.*

| if a fix lands on ... | it obliges a migration on ... | tracked at |
| --- | --- | --- |
| `checkpoint` | `drain` | `history/0004-drain.md` |
| `compaction` | `routing` | `history/0009-routing.md` |
| `dispatch` | `quota` | `history/0016-quota.md` |
| `rollup` | `retention` | `history/0018-retention.md` |
| `routing` | `audit` | `history/0013-audit.md` |
| `watermark` | `digest` | `history/0003-digest.md` |

A migration is obliged, not optional: the destination stage's own history record
documents the change it must accept once the source stage's fix lands. The record
itself is the citation; nothing here restates its content.
