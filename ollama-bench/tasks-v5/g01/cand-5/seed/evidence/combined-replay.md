# Combined replay: cross-source sequence C-88

This replay was prepared to exercise interactions between all current source
families. It is presented as a chronological review because a source-local
answer is not enough: canonical names decide which position map and which
source-specific key table are used.

1. `svc` has `req` +2 add with label `API`. This creates service and requests.
2. `core` has `compile` +5 add with label `Build`. This creates platform and
   build after service.
3. `service` has `request` -1 remove with label `api`. This updates service's
   first entry by +1 and does not move it.
4. `platform` has `compilation` -2 adjust with label `Compiler`. This updates
   platform build by -2.
5. `ui` has `draw` 0 hold with labels `Paint` and ` paint `. This creates
   frontend and its render entry with total zero, occurrence one, label paint.
6. `batch` has `task` 7 add with label `Queue`. This creates worker and jobs.
7. `web` has `paint` 4 void with label `Admin`. It merges into frontend but
   does not create or update an entry.
8. `jobs` has `job` -3 remove with label `Done`. It updates worker jobs by +3.
9. `svc` has `cfg` 0 add with no labels. It creates service config after the
   already existing requests key.
10. `core` has `lat` 9 ignore with label `Nope`. It has no effect beyond the
    already existing platform bucket.

The final outer order is service, platform, frontend, worker. Within service,
requests precedes config. Platform contains build only. Frontend contains
render only. Worker contains jobs only. The review is intentionally long enough
to make it unsafe to answer by considering one source family in isolation.
