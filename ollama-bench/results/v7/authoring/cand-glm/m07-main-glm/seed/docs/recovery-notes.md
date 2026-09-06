# Recovery notes - support-tooling example

The support tooling calls the `coalesce` operation when a customer asks why a recovered
handle looks unchanged after a restart. It never calls the bound pipeline stage directly -
see `handle_bridge.py`'s own docstring for how that stage is identified, and why this page
does not name it.

    from ember.ext.op_table import resolve
    op = resolve("coalesce")
    op("h-4471", payload={"resumed": True})

The audit trail records the call as `{"op": "coalesce", ...}`; `trail_writer.serialize_call`
rejects any other name.
