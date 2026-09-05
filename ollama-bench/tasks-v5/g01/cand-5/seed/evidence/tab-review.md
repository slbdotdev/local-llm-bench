# Tab and edge-space review

Relay input uses the ordinary ASCII space as presentation padding. It does not
declare all Unicode or Python whitespace to be padding. Source, key, and label
normalization therefore uses the literal character set containing one space at
both edges, followed by case folding where the field requires it.

For sources, ` core ` is platform, `core` is platform, ` core\t` is the unknown
source `core\t`, and `\tcore` is the unknown source `\tcore`. Source names are
not case-folded. For keys under platform, ` compile ` is build, `Compile` is
build after casefold, `compile\t` is `compile\t`, and `\tcompile` is
`\tcompile`. Keys are case-folded after edge-space removal.

For labels, ` Owner ` is owner, `OWNER` is owner, `owner\t` is `owner\t`, and
` ` becomes empty and is discarded. A tab-only label becomes the nonempty value
`\t`. Interior spaces are retained: `high priority` remains `high priority`.

The tab cases are ordinary valid strings, not malformed data. They make broad
`strip()` a plausible near-miss. The source and key behavior must not be
silently unified: sources use exact alias lookup without casefold, while keys
and labels use casefold as stated.
