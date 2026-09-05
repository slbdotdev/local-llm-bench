# Replay timeline review

The operations team records a timeline with source spelling, action, key, raw
delta, and labels. The adapter intentionally does not emit a timeline; it
folds the timeline into the public ledger. The timeline is still useful for
checking that no stage is accidentally applied globally or out of order.

At t1, ` core ` reports void compile 7 with `internal`. At t2, `svc` reports
add req 3 with `API`. At t3, `platform` reports hold compilation 8 with
`Build`. At t4, `service` reports remove request -2 with `Retry`. At t5, `core`
reports add build 0 with `build`. At t6, `svc` reports ignore err 4 with
`private`. At t7, `platform` reports adjust compile -1 with `Compiler`.

The timeline yields platform first, service second. Platform build is created at
t3 by hold, then receives t5 and t7, so its total is -1, count three, and its
labels are build then compiler. The t1 void does not seed an old label or key.
Service requests is created at t2 and receives t4, for total 5 and count two;
labels are api then retry. The t6 ignore is invisible.

The same source can be written through an alias or long spelling at different
times without changing its established position. The same key can be written
through a global alias or source-specific alias without changing its entry
position. The timeline is deliberately chronological because sorting by final
canonical values would answer a different question.

The review also confirms that source bucket creation precedes the t1 rejection:
platform is present even before its first accepted change at t3.
