# 2025-11 source review

The source alias table was reviewed after three exporter teams chose different
names for the same owner. The accepted aliases are `core` to `platform`, `svc`
to `service`, `web` and `ui` to `frontend`, and `jobs` and `batch` to `worker`.
The lookup is exact after removing ordinary ASCII spaces at the edges. It does
not case-fold source names, remove tabs, or chase a target through the table a
second time.

The exactness is deliberate. Source identifiers are not prose and some teams
use case or tab characters to distinguish external systems. Only the known
presentation spaces are removed. Unknown names survive in their trimmed form,
including the empty string.

The alias target is used for both outer identity and the source-specific key
alias table. A short source page and a long source page therefore share one
position map. A later alias cannot move a bucket or reset its entries.
