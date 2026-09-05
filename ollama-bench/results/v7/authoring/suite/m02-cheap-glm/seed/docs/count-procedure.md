# Count procedure - Friday shelf figure

Owner: stockroom lead. This is the physical side of `data/inventory.csv`;
the code in this repository never performs a count.

1. Counting starts 07:30, before opening, and walks the shelves in
   inventory file order. A row is recounted on the spot when the counter
   is unsure; the file order is the walking order so the two lists can be
   compared line by line.
2. The counter writes the counted figure next to the system figure and
   initials the row. A figure the counter could not confirm is written as
   the system figure with a question mark, never left blank.
3. Differences under three units are noted and accepted. Three units or
   more on any row, or any pattern of differences, goes to the stockroom
   lead the same morning.
4. Once the sheet is initialled by the stockroom lead, the counted figures
   replace the previous ones in `data/inventory.csv` and the old sheet is
   filed. Full stock-takes (all twelve SKUs, every bin) happen at the end
   of August and are kept under `data/` as their own dated file.
5. The file's row order is the shelf order. Rows are not re-sorted when
   figures are replaced, because the pick lists and the shelf labels both
   follow the same order.
