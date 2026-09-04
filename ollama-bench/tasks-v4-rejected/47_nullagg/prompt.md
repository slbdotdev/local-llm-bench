Create `nullagg.py` in the current directory: a small NULL-tolerant query API over an
in-memory table. A **row** is a `dict` mapping column name (a `str`) to a value. A row that
is missing a key is treated exactly as if the key were present with the value `None`
("NULL"). Values are only ever `None`, `bool`, `int`, `float` (never NaN) or `str`.

```python
class Table:
    def __init__(self, rows=()): ...        # rows: an iterable of dicts; copied in
    def rows(self) -> list[dict]: ...       # the current rows, in order
    def order_by(self, *keys) -> "Table": ...
    def distinct(self, *cols) -> "Table": ...
    def group_by(self, cols, **aggs) -> "Table": ...
    def having(self, pred) -> "Table": ...

# aggregate constructors (used as keyword arguments to group_by)
count_star()                       count(col)      sum_(col)   avg(col)
min_(col)   max_(col)              any_(col)       every(col)

# predicate constructors (used as the argument to having)
eq(col, value)   ne(col, value)   lt(col, value)   le(col, value)
gt(col, value)   ge(col, value)   is_null(col)
and_(*preds)     or_(*preds)      not_(pred)
```

Every `Table` method returns a NEW `Table` and never mutates the receiver, so calls chain:
`t.distinct("a").order_by("a").rows()`. `Table.rows()` returns a list of dicts equal to the
table's rows in their current order.

## The value order

Sorting and `min_`/`max_` use one fixed **ascending total order** over non-`None` values:

1. Each value has a *type group*: `str` values are group 1, everything else (`bool`, `int`,
   `float`) is group 0. If two values are in different groups, the smaller group number
   comes first (so every number sorts before every string). This never raises.
2. Within a group, values are compared with Python `<`. Two values `a`, `b` for which
   neither `a < b` nor `b < a` count as EQUAL for ordering (so `1`, `1.0` and `True` are
   mutually equal here).

## order_by(*keys)

Each argument is a sort key, given as either

* `"col"` -- ascending, default null placement, or
* `("col", direction)` where direction is `"asc"` or `"desc"`, default null placement, or
* `("col", direction, nulls)` where nulls is `"first"` or `"last"`.

Sort by the keys in order (the first argument is the primary key). The sort is STABLE: rows
that compare equal on every key keep their relative input order. `order_by()` with no keys
returns the rows unchanged.

For one key: `None` values are grouped together and placed either at the FRONT
(`"first"`) or at the BACK (`"last"`) of that key's ordering -- this is an absolute position
in the output and is NOT flipped by `direction`. Non-`None` values are compared with the
ascending total order above, reversed when direction is `"desc"`.

**The DEFAULT null placement depends on the direction**: `"asc"` defaults to `"last"` and
`"desc"` defaults to `"first"`. (So by default nulls are at the end of an ascending sort and
at the start of a descending sort; an explicit third element overrides that.)

## distinct(*cols)

Returns the rows whose combination of values in `cols` is seen for the first time, in the
original order (first occurrence wins, later duplicates are dropped). Two rows are duplicates
iff for every column in `cols` their two values are equal, where `None` IS EQUAL to `None`
(NULLs do not make rows distinct), and non-`None` values are compared with Python `==` (so
`1`, `1.0` and `True` are equal here too). The rows returned are the FULL original rows, not
projected to `cols`. At least one column is always given.

## group_by(cols, **aggs)

`cols` is a list of column names (possibly empty). The group key of a row is the tuple of its
values for `cols`, with the same equality rule as `distinct` (`None` equals `None`). Groups
are emitted in order of first appearance of their key.

* If `cols` is EMPTY there is exactly one group containing all rows -- **including when the
  table has zero rows**, in which case `group_by([], ...)` still emits exactly one output
  row, whose aggregates are computed over an empty group.
* If `cols` is non-empty and the table has zero rows, the result has zero rows.

Each output row is a dict with one key per column in `cols` (holding that group's key value)
plus one key per keyword argument, holding the value of that aggregate over the group's rows.
Aggregate names never collide with column names.

Aggregates (`col` values that are `None` are called *nulls*; all other values are *inputs*):

* `count_star()` -- the number of rows in the group (nulls included). Always an `int`.
* `count(col)` -- the number of inputs, i.e. rows whose `col` is not `None`. `0` for a group
  whose `col` is `None` in every row, and `0` for an empty group.
* `sum_(col)` -- Python `sum` over the inputs; `None` if there are no inputs.
* `avg(col)` -- `sum(inputs) / len(inputs)`, a true division (so a `float`); `None` if there
  are no inputs. **Nulls are not counted in the denominator.**
* `min_(col)` / `max_(col)` -- the smallest / largest input under the ascending total order
  above; `None` if there are no inputs.
* `any_(col)` / `every(col)` -- three-valued aggregates over a column whose values are only
  `True`, `False` or `None`. Here nulls ARE looked at:
  * `every(col)` is `False` if any value is `False`; otherwise `None` if any value is `None`;
    otherwise `True` -- so `every` over a group with no rows is `True`.
  * `any_(col)` is `True` if any value is `True`; otherwise `None` if any value is `None`;
    otherwise `False` -- so `any_` over a group with no rows is `False`.

`sum_`/`avg` are only ever applied to columns whose non-`None` values are numbers, and
`any_`/`every` only to columns whose values are `True`/`False`/`None`.

## Predicates and having(pred)

A predicate is a callable `pred(row)` returning one of three values: `True`, `False` or
`None` (`None` means UNKNOWN). `having(pred)` keeps a row **only when `pred(row)` is `True`**
-- both `False` and UNKNOWN drop it. (It is a plain filter over the table's current rows, so
it is normally chained after `group_by` and reads the aggregate columns by name.)

Let `a` be the row's value for `col` and `v` the constant:

* `eq` / `ne`: UNKNOWN if `a is None`; otherwise `a == v` / `a != v` with plain Python
  semantics (so with `v = None` and a non-`None` `a`, `eq` is `False` and `ne` is `True`).
* `lt` / `le` / `gt` / `ge`: UNKNOWN if `a is None`, if `v is None`, **or if `a` and `v` are
  in different type groups** (a number against a string); otherwise the Python comparison.
  Note this differs from sorting: ordering places numbers before strings, but a comparison
  predicate across the two groups is UNKNOWN.
* `is_null(col)`: `True` iff `a is None`, `False` otherwise. It never returns UNKNOWN.
* `and_(*preds)`: `False` if any argument is `False`; otherwise UNKNOWN if any is UNKNOWN;
  otherwise `True`. `and_()` with zero arguments is `True`.
* `or_(*preds)`: `True` if any argument is `True`; otherwise UNKNOWN if any is UNKNOWN;
  otherwise `False`. `or_()` with zero arguments is `False`.
* `not_(pred)`: `True` -> `False`, `False` -> `True`, UNKNOWN -> UNKNOWN.

## Examples

```python
from nullagg import Table, count_star, count, sum_, gt

rows = [{"g": "a", "x": 3}, {"g": "b", "x": None}, {"g": "a", "x": 1},
        {"g": "b", "x": 5}, {"g": "a", "x": None}]

Table(rows).order_by("x").rows() == [
    {"g": "a", "x": 1}, {"g": "a", "x": 3}, {"g": "b", "x": 5},
    {"g": "b", "x": None}, {"g": "a", "x": None}]      # asc -> nulls last, stable

Table(rows).group_by(["g"], n=count_star(), c=count("x"), s=sum_("x")).rows() == [
    {"g": "a", "n": 3, "c": 2, "s": 4},
    {"g": "b", "n": 2, "c": 1, "s": 5}]                # groups in first-appearance order

Table(rows).distinct("g").rows() == [{"g": "a", "x": 3}, {"g": "b", "x": None}]

(Table(rows).group_by(["g"], s=sum_("x")).having(gt("s", 4)).rows()
 == [{"g": "b", "s": 5}])
```

Write a few quick checks of your own and run them with `python`, then reply "done".
