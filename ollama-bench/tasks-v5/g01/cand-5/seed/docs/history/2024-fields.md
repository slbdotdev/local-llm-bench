# 2024-08 field migration

The importer changed from tuple values to dictionaries with explicit names.
The input field names stabilized as `source`, `changes`, `key`, `delta`,
`action`, and `labels`. The public output intentionally uses `source`,
`entries`, `key`, `total`, `occurrences`, and `labels`; raw input fields are not
copied through. A change is valid even when its key or label is an empty string.

This field migration is the reason validation was moved outside the reducer.
The reducer receives valid records and is allowed to use direct field access.
It must not invent defaults for missing fields, stringify integers, or turn
labels into a set. The benchmark uses the same valid-input boundary as the
production adapter.

The output list and every output dictionary are owned by the adapter. A caller
may hold a reference to the input batch and reuse it after transformation. The
adapter therefore reads label values but never appends to an input label list.
The first accepted change gets a new label list; a duplicate updates only the
output-owned list.
