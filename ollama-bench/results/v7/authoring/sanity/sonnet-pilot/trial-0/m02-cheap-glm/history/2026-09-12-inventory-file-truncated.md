# 2026-09-12 - inventory file truncated by a bad copy

What happened: a copy of `data/inventory.csv` made on a memory stick came
back with the last four rows missing. The low-stock list printed four
items short, which was noticed the same morning because the buyers'
order came in under the shelf walk.

What was done: the shelves were walked again the same afternoon (count
procedure, step 1) and the file was restored from the initialed count
sheet, row order included. No row was re-sorted while restoring, because
the file order is the shelf order and the pick lists depend on it.

Why it is recorded here: two habits came out of it. First, the file's
row order is part of the data - restoring "the same rows" in a different
order would have been a second mistake. Second, a short list is itself a
symptom: if the count line ever disagrees with the shelf walk, suspect
the file before the shelves.

The memory stick is no longer used for inventory files.
