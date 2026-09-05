# Freshness review: ownership probes

The input batch contains nested mutable lists at every API boundary. A correct
adapter may read these values but must not use them as output containers.

Probe F-1 calls the adapter with one record and one change, then appends a new
change to the returned entry's labels. The source record's `labels` remains the
original list. Probe F-2 changes the returned bucket's entries list and checks
that the input record's `changes` list has the original length. Probe F-3
changes a returned entry's total and verifies that the input delta is unchanged.

Probe F-4 calls the adapter twice with the same input. The two result trees may
contain equal values but are distinct mutable containers. Probe F-5 transforms
two records with the same canonical source and verifies that the one bucket's
entries list is not shared with an unrelated empty bucket. Probe F-6 transforms
an empty input and then mutates the returned list; a later empty call still
returns an independent empty list.

These probes do not require copying immutable strings or integers. They do
require constructing each public list and dictionary and copying accepted
labels into output-owned lists. A shallow return of an input record is not a
valid public result even if its values look correct before a caller mutates it.
