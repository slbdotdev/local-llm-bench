# Source/key scope review

The reducer maintains two nested identity dimensions. The outer dimension is
canonical source; the inner dimension is canonical key within that source. A
key name does not identify one global entry. This matters because every source
family can report `error`, `latency`, or an unknown name at the same time.

The sequence `svc: err +1`, `core: err +2`, `service: warn +3`, `platform: warn
+4` produces service error and warning, then platform error and warning. The
service aliases merge its two records, and the platform aliases merge its two
records, but no service entry merges with a platform entry. Each source's inner
order follows its own first accepted key.

A source-specific alias uses the outer canonical source as its table selector.
The raw source `svc` therefore enables the service mapping for `req`; the raw
source `core` enables platform mapping for compile. Using the raw alias as a
selector leaves plausible but incorrect unexpanded keys.

Labels have the same nested scope. Equal canonical label strings on entries in
different sources are independent lists. Labels on two keys in one source are
also independent. Only repeated accepted occurrences of one canonical source
and key merge label state.

The scope review rejects a single global accumulator even when all totals are
otherwise correct. It also rejects rebuilding each source from sorted raw
records because that loses the outer temporal order.
