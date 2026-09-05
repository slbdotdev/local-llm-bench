# Operations calendar

*Deploy-freeze windows for the northgate-relay pipeline. Owner: Capacity Planning.*

**This calendar is the authoritative schedule of deploy-freeze windows.** A freeze that
is not entered here is not in force, whatever a meeting invite, a handover note or a
chat thread says. When any other document disagrees with this calendar about a freeze,
the calendar is right and the other document is stale.

## How windows are entered

A window is entered by Capacity Planning after the train review that authorised it, and
never retroactively. Entries are never removed: a window that was entered and later
cancelled would be struck through and kept, so the absence of a month from this table
means exactly that no window was ever entered for it.

## Freeze windows

| window starts (UTC) | duration | reason |
| --- | --- | --- |
| 2034-09-14 | 24h | quarterly release train |
| 2034-10-05 | 24h | storage rollover on the evidence store |
| 2034-12-04 | 24h | quarterly release train (absorbs the cancelled November train) |
| 2034-12-19 | 72h | year-end change freeze |
| 2035-01-15 | 24h | manifest schema migration |
| 2035-02-20 | 24h | evidence-store failover drill |
| 2035-03-11 | 24h | quarterly release train |

There is no other table of freeze windows. Routine maintenance windows that do not
freeze deploys are tracked in the ticket system and deliberately do not appear here.
