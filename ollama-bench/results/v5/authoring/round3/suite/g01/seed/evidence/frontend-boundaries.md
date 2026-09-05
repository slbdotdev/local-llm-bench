# Frontend boundary cases

Frontend is the target of `web` and `ui`. The long spelling with ordinary edge
spaces has the same identity. The source alias lookup is exact after the edge
space operation: `WEB`, `web\t`, and `\tweb` are unknown source strings.

The local key table maps paint and draw to render. Global aliases still apply
to keys such as warn, err, latency, duration, and config. A global alias target
is not run back through a local table. A raw `draw` is local render; a raw `warn`
is global warning. Unknown keys are case folded but not otherwise invented.

The UI commonly sends adjacent accepted changes with labels `Frame`, `frame`,
and ` frame `. The resulting label list contains one frame. It sometimes sends
a tab-prefixed label; that remains a separate canonical value. It also sends a
space-only label, which is dropped. The accepted change's occurrence still
counts when every label is dropped.

An operations dashboard may place a void paint change before an accepted paint
change. The void does not reserve render's entry position and its label is not
seen. A hold render change is different: it creates or updates render with
zero contribution and an occurrence. A remove with a negative delta contributes
positive amount by signed multiplication.

The frontend result is frequently displayed beside service and platform. Its
outer position is determined by the first canonical frontend record, not by the
alphabetical name frontend or by when its first accepted key appears.
