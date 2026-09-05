# Migration alias matrix: names seen in archived feeds

The archive contains several source and key spellings. The table below is a
review source, not a request to invent more aliases. Only the listed source
aliases and key aliases are current. An unknown spelling is retained after the
normalization steps stated by release 3.2.

| raw source | canonical source | raw key | canonical key in that source |
| --- | --- | --- | --- |
| ` core ` | `platform` | ` compile ` | `build` |
| `platform` | `platform` | `compilation` | `build` |
| ` svc ` | `service` | `REQ` | `requests` |
| `service` | `service` | `request` | `requests` |
| ` web ` | `frontend` | `paint` | `render` |
| `ui` | `frontend` | `DRAW` | `render` |
| `jobs` | `worker` | `task` | `jobs` |
| ` batch ` | `worker` | `job` | `jobs` |
| `unknown` | `unknown` | ` warn ` | `warning` |
| ` CORE ` | `CORE` | `\tErr` | `\terr` |

The source lookup is exact after ASCII-space edge removal and is not case
folded. The key lookup is case folded after ASCII-space edge removal. A tab in a
key or source remains part of that value and prevents an alias match when it is
present at an edge.

The source-specific column is evaluated using the canonical source, not the raw
source. Thus a `core` record can use `compile` and a `svc` record can use
`request`. Global aliases are evaluated before this column, and each table is
looked up once.
