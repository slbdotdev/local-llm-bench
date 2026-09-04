Create `query.py` in the current directory with a function:

    run(rows, spec) -> list of dicts

`rows` is a list of dicts representing an in-memory table (each dict is one row; a row that is missing a key is treated as if the key were present with value `None`). `spec` is a dict whose keys are all optional: `where`, `group_by`, `select`, `order_by`, `limit`, `offset`. `run` must not mutate `rows` or `spec`, and must return a new list of new dicts. The grader only uses column names that are strings and row values that are None, int, float or str.

Evaluation order: (1) filter the rows with `where`; (2) group the filtered rows; (3) project each group/row with `select`; (4) sort with `order_by`; (5) apply `offset`; (6) apply `limit`.

## where

`spec["where"]` is a predicate tree. A predicate is a dict, evaluated recursively to one of three values: True, False or UNKNOWN.

- Comparison: `{"op": "eq"|"ne"|"lt"|"le"|"gt"|"ge", "col": <name>, "value": <constant>}` — compares the row's value for `col` with the constant.
- Null test: `{"op": "is_null", "col": <name>}`.
- Conjunction/disjunction: `{"op": "and"|"or", "args": [<predicate>, ...]}`.
- Negation: `{"op": "not", "arg": <predicate>}`.

Rules:

- Three-valued logic: any comparison involving None is UNKNOWN. Concretely: if the row's value for `col` is None (which includes a missing key), `eq`, `ne`, `lt`, `le`, `gt`, `ge` evaluate to UNKNOWN. `is_null` is the only way to test for None: it is True iff the value is None, and it never returns UNKNOWN.
- If the row's value is not None: `eq` is True iff `value == constant`, and `ne` is True iff `value != constant` (Python semantics; so with constant None, `eq` is False and `ne` is True for a non-None value). `lt`/`le`/`gt`/`ge` evaluate to UNKNOWN if the two values are not mutually comparable with `<` (e.g. a str compared with a number, or a comparison whose constant is None); otherwise they give the result of the corresponding Python comparison.
- `not`: True -> False, False -> True, UNKNOWN -> UNKNOWN.
- `and` over its args: False if any arg is False; otherwise UNKNOWN if any arg is UNKNOWN; otherwise True. `and` over zero args is True.
- `or` over its args: True if any arg is True; otherwise UNKNOWN if any arg is UNKNOWN; otherwise False. `or` over zero args is False.
- A row is kept iff its `where` predicate evaluates to True — UNKNOWN drops the row. If `spec` has no `where`, every row is kept.

## grouping

The query is grouped iff `spec` has a `group_by` (a list of column names) OR its `select` contains at least one aggregate spec (see below).

- If `group_by` is present: the group key of a row is the tuple of the row's values for the `group_by` columns; two rows are in the same group iff their keys are equal (None equals None, so rows whose keys are all None form one group). Groups are emitted in order of first appearance of their key among the filtered rows.
- If `group_by` is absent but `select` contains an aggregate: there is exactly one group containing all filtered rows — even when there are zero filtered rows.
- Otherwise: no grouping; each filtered row produces one output row.

## select

`spec["select"]` is a list of output column specs. Each spec is a dict; a spec that has a `"fn"` key is an aggregate spec, otherwise it is a plain-column spec of the form `{"col": <name>}`.

- Plain column: in a grouped query its value comes from the first row of the group (in filtered-row order; a plain column evaluates to None if the group has no rows); in an ungrouped query it is the row's value for that column (None if the key is missing).
- `{"fn": "count_star"}`: the number of rows in the group.
- `{"fn": "count"|"sum"|"min"|"max"|"avg", "col": <name>}`: an aggregate over the group's rows. Every aggregate except `count_star` ignores None inputs (rows whose value for `col` is None, including missing keys, are not inputs at all):
  - `count`: how many rows in the group have a non-None value for `col`.
  - `sum`: exactly Python `sum(values)` over the non-None values; None if there are none (empty group or all values None).
  - `avg`: exactly `sum(values) / len(values)` over the non-None values (true division, so a float); None if there are none.
  - `min` / `max`: exactly Python `min(values)` / `max(values)` over the non-None values (None excluded from the ordering); None if there are none.

Output row shape: one key per select spec. A plain-column spec contributes the key `<col>`; an aggregate spec contributes the key `count(*)` for `count_star` and `<fn>(<col>)` for every other aggregate (e.g. `count(x)`, `sum(amount)`, `avg(score)`).

If `spec` has no `select`: for a grouped query each output row contains only the `group_by` columns (with their group-key values); otherwise each output row is a shallow copy of the corresponding filtered row with exactly its original keys.

## order_by

`spec["order_by"]` is a list of `(column, direction, nulls)` tuples, where direction is `'asc'` or `'desc'` and nulls is `'nulls_first'` or `'nulls_last'`. Sorting applies to the OUTPUT rows (after projection): the column names a key of an output row, and an output row without that key counts as None. Sort by the entries in order — the first entry is the primary key. Rows that compare equal on all entries keep their relative order (stable sort). For each entry: every None goes before all non-None values with `nulls_first` and after all non-None values with `nulls_last`, regardless of direction; non-None values are compared with Python `<`, reversed for `'desc'`. Without `order_by`, output rows keep their natural order (filtered-row order, or group emission order for grouped queries).

## limit and offset

Applied last, after sorting: first drop the first `offset` output rows (default 0), then keep at most `limit` rows (default: keep all). `limit: 0` yields no rows; an `offset` at or past the number of rows yields no rows.

Write a few quick checks of your own and run them with `python`, then reply "done".