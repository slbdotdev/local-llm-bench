# Evidence index and review ownership

The evidence directory is organized by the questions the release review asked.
The service, platform, frontend, and worker reviews are importer-specific
source material. The operations, action, zero, and rejected-label reviews cover
policy. Migration-aliases, key-boundaries, and tab-review cover identity. The
ordering, alias-order, duplicate, and sequence reviews cover position and
stage order. Freshness and output-boundaries cover ownership and shape.

Each review is a current-release observation unless it is under `docs/history`,
where the release number and superseded status are explicit. Repeated facts are
intentional cross-checks from different callers: a model that reads only one
module can choose a plausible adjacent behavior, while a conforming adapter
must reconcile the independent views.

The project does not ask for malformed-input behavior, error messages, a CLI,
or file I/O. Every record and change described by these reviews has the valid
schema. The only variation is ordinary string content, signed integer value,
action, list order, and record order. The task is a deterministic fold over
that material.

The final release review signs off only when these invariants hold together:
bucket lifecycle before policy; policy before key and labels; canonical source
before local key aliases; signed arithmetic with accepted zero cases; first
seen positions for all three list levels; exact public shape; and fresh output
ownership. No hidden convention is needed beyond the stated release rules.
