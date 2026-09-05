# Glossary - workshop stockroom

The words used in this repository, and what they mean here.

- **SKU** - the stock code, `QM-` followed by four digits. One physical
  kind of item. There is no leading-zero form and no alias; a SKU is
  exactly the string in the inventory file.
- **On hand** - the quantity the current inventory file says is on the
  shelves. A system figure, refreshed by the Friday count.
- **Counted** - the figure a human wrote on a count sheet. The August
  full stock-take keeps its own dated file; a count is not "on hand"
  until it has replaced the file figure.
- **Reorder point** - the whole-number quantity per SKU at which the next
  order must be raised. Set at the quarterly review by Data Stewardship.
- **Low stock** - on hand at or below the reorder point (stocking policy,
  rule 2). The boundary is inclusive at the point; there is no cushion.
- **Pick list** - the list the stockroom walks the shelves with. Its
  order is the inventory file's row order, which is the shelf order.
- **Stock-take** - a full count of every SKU in every bin, at the end of
  August. Kept as its own dated file under `data/`.
- **Buyer summary** - the monthly reorder suggestion the buyers receive,
  rendered by `report.py` and sent with the `REORDER SUGGESTION` heading.

Terms not on this list mean what the docs that introduce them say they
mean, and nothing else.
