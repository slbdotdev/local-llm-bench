# Platform import review: build batch P-04

The platform exporter calls its owner `core` in early records and `platform` in
later records. Both spellings refer to one source bucket. Source aliases are
case-sensitive, so `CORE` would be an unknown source rather than another
spelling of `core`. Ordinary spaces around `core` are removed; a tab is data.

The first record contains `compile` delta 12 action `add`, then `lat` delta 4
action `remove`. The canonical source is `platform`; `compile` is first
case-folded and does not match a global alias, then the platform-specific map
turns it into `build`. `lat` becomes global key `latency`. Entries appear in
the order `build`, `latency`, regardless of which total is larger.

The second record contains `compilation` delta -2 action `adjust`, labels
`Compiler`, and `build` delta 0 action `add`, labels `compiler` and `Fast`. The
first change is the same platform `build` key and contributes -2. It updates
the existing first entry, making its total 10 and occurrences 2. The second
change is an accepted zero contribution and also updates the first entry,
making total 10 and occurrences 3. Labels are `["compiler", "fast"]` after
canonicalization and first-seen deduplication.

The third record is ` platform ` with a `void` change for `CFG`, delta 88,
label `Should-not-show`. It creates no entry and does not change the platform
bucket. Since `cfg` is a global alias, the hypothetical key would be `config`,
but rejection happens first and the key is never observed.

The fourth record is an empty `platform` page. It has no effect on existing
entries or order. If it were first, it would still leave an empty platform
bucket. A dictionary built only from nonempty entries would be wrong.

The batch review uses large signed deltas in other pages, including a remove of
-5 which contributes +5. There is no absolute-value rule and no clamping at
zero. These records are valid input examples, not malformed stress cases.
