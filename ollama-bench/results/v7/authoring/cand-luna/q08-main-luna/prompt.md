# Replay the handoff chain

You are in the root of the `orison-thread` checkout.  Produce one new file named
`handoff.txt`; do not modify or delete any existing file and do not create anything else.

Use the first 22 component entries, in exactly the order they appear in
`config/manifest.json`.  The first marker is the `@START` marker in the project's material.
For each component, do these actions in order:

1. In that component's document, find the one route row whose incoming marker equals the
   marker produced by the preceding component.  At step 1, use the initial marker.  A row has two
   labelled candidate destinations: a branch tag immediately followed by its destination, then
   another branch tag immediately followed by its destination.
2. Read that component's branch tag from its Python module and its certificate (`affirm` or
   `invert`) from its history entry.  If the certificate is `affirm`, select the destination
   carrying the module's branch tag.  If it is `invert`, select the other destination on the
   matched row.  The selected destination is the marker for the next step.
3. Carry that selected marker forward as the lookup key for the next component.  Do not restart a
   lookup from the initial marker.

Write exactly these five `key: value` lines to `handoff.txt`, in this order.  The values are
the marker strings exactly as they appear in the material; do not add commentary or quotes:

    mark_05: <marker produced at step 5>
    mark_10: <marker produced at step 10>
    mark_15: <marker produced at step 15>
    mark_20: <marker produced at step 20>
    terminal_marker: <marker produced at step 22>

The five reported markers are the running results of one serial replay.  A marker from an earlier
component is not a substitute for the marker produced immediately before the component you are
reading.
