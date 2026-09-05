You are working in a snapshot of the `cinder-vault` repository.

The `dispatch` stage has no way to release capacity held by records that have waited too long.
Add one to it, in `src/cinder/dispatch_gate.py`, by giving the `DispatchLedger` class exactly these two
new methods and changing nothing else about the class's existing behaviour:

    def reap(self, ages):
        # `ages` maps a record key to that record's age in seconds, as an int.
        # A record whose age is strictly greater than the stage's `window_s` has waited too
        # long. Returns the number of records this call reaped, as an int.

    def active_count(self):
        # Returns, as an int, how many records currently count against the stage's `limit`.

A key in `ages` that the stage has never seen is ignored. A record that has already been reaped
is not reaped again, so calling `reap` twice with the same argument reaps nothing the second
time.

**What reaping does to a record is decided by this project's own documentation, not by you.**
The repository states its rule once and states it plainly; find it and implement exactly that.
Where two documents disagree, the repository's `README.md` says which kind of document wins, and
a history entry marked superseded is evidence of a past decision rather than an instruction.

Do not change any other file. Do not change the existing methods, the constructor, the module
constants, or `snapshot()`.
