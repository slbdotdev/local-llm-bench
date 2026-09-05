# Service boundary cases

The service owner has the largest number of archived naming variants. The
following records are taken from importer review and are kept as separate
cases because each boundary has a different result.

`svc` and ` svc ` canonicalize to service. `svc\t`, `\tsvc`, and `Svc` do not.
An unknown source is not rejected; it receives a bucket under the trimmed raw
value if ordinary edge spaces are present. Source aliases are not a general
case normalization feature.

For service keys, `req`, `request`, and ` requests ` canonicalize to requests;
`REQ` reaches the same result through casefold. `request\t` and `\trequest`
remain distinct values because the tab is not trimmed. `err` reaches global
error, while a source-specific table is only consulted after global mapping.

A service batch can contain a source-only record between two pages. It must not
reset the existing request entry. It can also contain `ignore` before `req`;
the ignored key does not reserve an entry position, so the accepted req starts
the list. A later `hold` for req updates that entry, contributes zero, and
appends accepted labels.

The service caller sends labels from multiple producers. `API`, `api`, and
` api ` become one label. `\tapi` is a second value, and ` ` disappears. Labels
are list data in first-seen order, not a bag. These cases are run after alias
expansion so the service-specific key table is selected by `service`.

The practical result is that the solver must keep source position maps and
entry position maps separate. A global key map would incorrectly merge `req`
with a similarly named key in another source, while a raw-source map would
incorrectly split aliases.
