The current directory already contains a small working ledger: `model.py` (parsing/validation), `engine.py` (applying entries to balances), `report.py` (fixed-width rendering) and `visible_test.py` (a few visible checks, currently all passing).

Extend all three modules to support **transfers** and a new currency, as specified below. Everything already described in `visible_test.py` and everything listed under "unchanged" below must keep working exactly as it does now. Do not edit `visible_test.py`; `python visible_test.py` must still print `ALL OK` when you are done. A hidden grader checks many more cases of both the old and the new behaviour, in all three modules.

## Unchanged contracts

- `model.LedgerError(ValueError)`; every rejection anywhere in the three modules raises `LedgerError` (never a bare `ValueError`, `KeyError`, `AssertionError`, ...).
- `model.parse_amount(text, currency) -> int` returns **minor units**. `text` must match `^\d+(\.\d+)?$` (no sign, no exponent, no spaces, `"1."` and `".5"` are invalid), it must have at most `model.CURRENCY_SCALE[currency]` digits after the point, the currency must be known, and the resulting value must be strictly positive; otherwise `LedgerError`.
- `model.format_amount(minor, currency) -> str` is the inverse formatting: an integer number of minor units rendered with exactly `CURRENCY_SCALE[currency]` decimal places (no decimal point at all when the scale is 0), with a leading `-` for negatives. Unknown currency raises `LedgerError`.
- `model.parse_entry(line) -> Entry`. Fields are separated by `|` and each field is stripped of surrounding whitespace. The date must be exactly `YYYY-MM-DD` and a real calendar date; the kind must be in `model.KINDS`; account names must match `^[a-z][a-z0-9_]*$`; the currency must be a key of `CURRENCY_SCALE`; the amount is parsed by `parse_amount`. Anything else raises `LedgerError`.
- `engine.apply_entries(lines) -> dict` maps account name -> dict of currency -> integer minor units. Blank/whitespace-only lines and lines whose first non-blank character is `#` are skipped. Dates must be non-decreasing over the whole sequence (equal dates are fine); an entry dated earlier than the previous entry raises `LedgerError`. `DEP` adds to the account's balance, `WDR` subtracts (balances may go negative). Accounts appear in the returned dict in first-appearance order, and the currencies inside one account in first-appearance order for that account.
- `engine.balance(state, account, currency) -> int` returns 0 for an account or currency that is absent.
- `report.render(state) -> str` renders fixed-width rows: `account.ljust(16) + " " + currency.ljust(3) + " " + amount.rjust(12)`, where `amount` is `model.format_amount(...)`. Nothing is ever truncated (a field longer than its width simply makes the line longer). The first line is that same row shape with `"ACCOUNT"`, `"CUR"`, `"AMOUNT"`; the second line is 33 `-` characters. Every line, including the last, is terminated by `\n`.

## 1. `model.py`

- Add `"BHD"` with scale **3** to `CURRENCY_SCALE`. The other three entries stay: `USD` 2, `EUR` 2, `JPY` 0. All arithmetic and formatting anywhere in the program must be driven by this table, not by a hardcoded 2.
- `model.KINDS` becomes exactly the tuple `("DEP", "WDR", "XFR")`.
- `model.Entry` gains a sixth and last field, `dest`, defaulting to `None`, so its fields are `date, kind, account, amount, currency, dest` and `Entry("2024-01-01", "DEP", "a", 1, "USD")` still works.
- A `DEP` or `WDR` line has exactly 5 fields, `DATE|KIND|ACCOUNT|AMOUNT|CURRENCY`, and `parse_entry` returns it with `dest=None`.
- An `XFR` line has exactly 6 fields, `DATE|XFR|ACCOUNT|AMOUNT|CURRENCY|DEST`, where `DEST` is the destination account and is validated by the same rule as `ACCOUNT`. `parse_entry` returns it with `dest` set to that name.
- `LedgerError` for: a line with fewer than 5 or more than 6 fields; an `XFR` line with 5 fields; a `DEP`/`WDR` line with 6 fields; a `DEST` that is empty or does not match the account pattern; a `DEST` equal to `ACCOUNT`.

## 2. `engine.py`

- `apply_entries` handles `XFR`: it moves `amount` minor units of `currency` out of `account` and into `dest`. The source account (and its currency key) is created/updated **before** the destination account, so a destination account that is new appears after the source in the returned dict's order.
- **Overdraft**: a transfer may not overdraw the source. If, at the moment the transfer is applied, the source account's balance in that currency is less than the transfer amount, raise `LedgerError` and do not return a state. A source with no balance at all in that currency counts as 0, so any transfer from it is an overdraft. Transferring exactly the whole balance is allowed and leaves the source at 0. The check is per account **and** per currency: a big `EUR` balance does not fund a `USD` transfer. Only `XFR` is checked this way; `WDR` may still drive a balance negative.
- New function `engine.totals(state) -> dict` mapping currency -> the sum of that currency's balance over every account, in minor units. The keys are in first-appearance order: iterate the accounts in `state`'s own order and, inside each account, its currencies in that account's own order. `totals({}) == {}`.

## 3. `report.py`

- The rows are now **sorted**: by account name ascending (plain string comparison), ties broken by currency code ascending. Every `(account, currency)` pair present in `state` is rendered, including ones whose balance is 0.
- After the rows, `render` appends a second line of 33 `-` characters, and then one row per currency **in the order given by `engine.totals(state)`** (first-appearance order, *not* sorted), using the literal account name `TOTAL` and `format_amount` of that currency's total.
- So the output is: header line, rule line, the sorted rows, a rule line, the TOTAL rows. For an empty state that is just the header line and two rule lines.

## Worked examples

```python
>>> model.parse_entry("2024-03-01|XFR|alice|1.250|BHD|bob")
Entry(date='2024-03-01', kind='XFR', account='alice', amount=1250, currency='BHD', dest='bob')
>>> model.parse_entry("2024-03-01|WDR|alice|4000|JPY")
Entry(date='2024-03-01', kind='WDR', account='alice', amount=4000, currency='JPY', dest=None)
>>> model.format_amount(-1250, "BHD")
'-1.250'
```

```python
>>> st = engine.apply_entries(["2024-01-01|DEP|zoe|100.00|USD",
...                            "2024-01-02|XFR|zoe|40.00|USD|amy"])
>>> st
{'zoe': {'USD': 6000}, 'amy': {'USD': 4000}}
>>> engine.totals(st)
{'USD': 10000}
>>> engine.apply_entries(["2024-01-01|DEP|zoe|1.00|USD",
...                       "2024-01-02|XFR|zoe|2.00|USD|amy"])
LedgerError: ...
```

```python
>>> print(report.render(st), end="")
ACCOUNT          CUR       AMOUNT
---------------------------------
amy              USD        40.00
zoe              USD        60.00
---------------------------------
TOTAL            USD       100.00
```

```python
>>> print(report.render({"b": {"JPY": 500}, "a": {"USD": -25, "JPY": 0}}), end="")
ACCOUNT          CUR       AMOUNT
---------------------------------
a                JPY            0
a                USD        -0.25
b                JPY          500
---------------------------------
TOTAL            JPY          500
TOTAL            USD        -0.25
```

Write a few quick checks of your own and run them with `python`, then reply "done".
