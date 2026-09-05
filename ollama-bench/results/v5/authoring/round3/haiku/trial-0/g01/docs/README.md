# Relay ledger project

This directory is the design record for Relay Ledger 3.2. The benchmark asks
for the behavior of the public record-to-ledger adapter, not for a copy of any
one source file. The adapter was kept deliberately small because it is used by
batch importers, but its contract is spread over the implementation modules,
the checked-in configurations, callers, fixtures, and release history.

The words “source” and “key” have different meanings. A source is the owner of
an entry and is visible in the outer result. A key identifies an entry within a
canonical source. A record creates its source bucket before any changes are
considered, so a record containing only changes that policy ignores still has a
visible empty bucket. Two spellings that canonicalize to one source share that
bucket and its entry order.

The adapter is a fold, not a sort. It walks records and changes from left to
right. The first accepted change for a canonical source/key creates an entry.
Later accepted changes update that entry in place. A policy-rejected change is
not an occurrence and contributes no labels, but it never cancels the source
bucket created by its record. This distinction is important to callers that use
an empty bucket to distinguish “reported nothing” from “not reported”.

This project has a few intentionally boring details that are still contract:
ASCII spaces around names are presentation noise, while tabs are data; keys
are case-insensitive using Python case folding; labels are case-insensitive too
but are retained in their first canonical spelling. Empty canonical labels are
discarded. Numeric deltas are not clamped, rounded, or converted to floats.

There are historical notes for the 2.x and 3.0 adapters. They are not alternate
answers. Use them to identify changes that the current release deliberately
made, especially around source aliases, ignored actions, and the point at which
labels are normalized. A caller may still mention an old name because old
imports are part of the supported input. A caller may not resurrect an old
ordering rule merely because it appears in a historical example.

The small package under `relay/` is explanatory source, not an installed
dependency. Its modules are intentionally separated along the same boundaries
used by the production package. The JSON files are release inputs. The fixture
and regression files are executable-test design records: a case omitted from a
single unit test is still part of the adapter contract when it is covered by a
fixture or regression note.

When reading, keep these questions separate:

1. Does the record create a bucket?
2. Does the change survive action policy?
3. What canonical source/key/labels does a surviving change have?
4. What weighted amount and occurrence does it add?
5. Where does the resulting object sit in the fresh output?

The answer must satisfy all five in sequence. The adapter does not expose
internal helper state, and no input object may be reused in its output.
