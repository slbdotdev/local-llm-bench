# report.py refactor - working notes

*(P. Ravindran, started 2026-07-18. Scratch notes, updated in place.)*

Why: render_legacy_summary re-reads the CSV itself, so the summary and the
on-screen check could disagree if the file changed between the two reads.
The new entry point takes the rows the caller already loaded.

Plan:

1. [x] render_summary(inventory, points, month) taking in-memory rows
2. [x] keep the heading format identical (buyers parse it)
3. [ ] port the buyer email template to the new heading call
4. [ ] port tests/test_report_legacy.py to render_summary, then delete it
5. [ ] remove render_legacy_summary one release after buyers switch

Status 2026-08-28: steps 1-2 are done and on disk. Steps 3-5 wait on the
buyers confirming the September summary format. Nothing else in the package
is touched by this refactor; stock.py is released and stays as it is.
