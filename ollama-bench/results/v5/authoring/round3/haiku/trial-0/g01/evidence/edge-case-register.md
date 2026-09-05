# Edge-case register E-3.2

The edge-case register is the data team's independent record of values that
must remain ordinary valid inputs. It is longer than a unit-test list because
each case is paired with the reason a conventional aggregation solution could
misread it.

An empty input is a fresh empty result. A record with source ` ` and no changes
creates a bucket whose source is empty. A record with source `svc` and no
changes creates service. A record with source `core` and only void changes
creates platform with no entries. These cases distinguish result lifecycle from
entry lifecycle.

An accepted empty-key change creates an entry whose key is empty. A rejected
empty-key change creates no entry. A label made only of spaces is discarded,
but a tab-only label survives because tab is data. Interior spaces are retained
in keys and labels. Source case is preserved for unknown names; key and label
case are folded.

Alias cases include `core`, ` core `, `CORE`, `core\t`, `svc`, `Svc`, `web`,
`ui`, `jobs`, and `batch`. Known forms merge only as stated by the exact table.
Key cases include err, warn, lat, dur, cfg, compile, request, paint, job, and
their source-local contexts. No alias is guessed from a similar word.

Arithmetic cases include every action with delta 0, a negative remove, an
adjustment that cancels an earlier amount, and a hold with a large value. Counts
are accepted observations, never nonzero amounts. Label cases put ignored and
void labels between accepted duplicates and verify that they remain absent.

Ordering cases put aliases after canonical names, duplicates after new keys,
empty records between pages, and the same raw key in two sources. The result
uses first canonical source, first accepted canonical key, and first canonical
label order at their respective scopes.

Ownership cases mutate returned buckets, entry lists, totals, and labels, then
compare the original nested input to a deep copy. The adapter owns all public
mutable containers and emits no position maps, raw fields, policy fields, or
page metadata.

The register is current 3.2 evidence. The 2.x and 3.0 history remains useful
only for identifying near-miss behavior; it is not a second valid answer.
