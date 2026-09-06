# Rename in flight: `snapshot()` to `stable_view()`

*State as of 2034-07-11. Delivery Engineering. Not scheduled.*

`snapshot()` returns a sorted view of the records a stage is holding and has never taken a
snapshot of anything. The name has sent two reviews looking for a persisted artifact that does
not exist, so the method is being renamed to `stable_view()` one stage at a time.

## Where it has got to

- Converted: `backfill_store`, on 2034-07-08.
- Not converted: every other stage module.
- `tests/test_backfill.py` still calls `snapshot()` on the converted stage and therefore
  fails. It is left failing on purpose. The tests are rewritten in the same change as the
  client migration, which has not been scheduled and is not this quarter's work.
- `src/tallow/compat_names.py` records the mapping. Nothing imports it yet.

Finishing the rename before the client migration lands would break the two integrations that
call `snapshot()` by name across the wire, which is why it has been left where it is rather
than carried through.
