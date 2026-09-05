# Authoring and maintenance notes

The project was split into small modules after the 3.2 incident review. Each
module owns one concern, but no module alone is the whole public contract. The
release-data view and JSON snapshots establish exact configuration. The stage
modules establish sequencing. Importer and replay records establish caller
observations. History explains superseded rules. Fixtures and evidence combine
the concerns.

A maintenance change must update all current evidence when it changes a public
rule. It must not silently copy an old rule from history. In particular, a
change to source alias matching affects outer identity and the local key-table
selector; a change to policy affects entries, totals, counts, and labels; a
change to label normalization affects both spelling and membership order.

The adapter is intentionally a pure transformation over valid in-memory
records. It does not read release JSON at runtime, consult the clock, use a
network, or depend on package installation. This makes batch and streaming
callers deterministic and lets the benchmark compare a local implementation
against an inline oracle.

The maintenance checklist for a new implementation is:

* construct or find a source bucket before iterating changes;
* use canonical source as outer identity and local alias-table selector;
* reject ignore and void before key or label work;
* accept hold even though its multiplier is zero;
* use signed integer multiplication and count accepted changes;
* preserve first-seen positions at source, key, and label scopes;
* normalize labels before deduplication and only after acceptance;
* allocate fresh public containers and emit exact fields only.

The checklist is not a replacement for the source tree. Its purpose is to
explain why the benchmark seed contains many independent records and why a
solver should read them before writing a short implementation. A task that
requires only one obvious file would not exercise the intended reconciliation
workload.
