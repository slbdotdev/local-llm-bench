"""Reconciliation report for the 2025-12-31 ledger close."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
import importlib.util
from pathlib import Path

from data.accounts import ACCOUNT_ALIASES
from data.rates import RATES_TO_USD

ROOT = Path(__file__).resolve().parent.parent
CUTOFF = "2025-12-31"


def _entries():
    for path in sorted((ROOT / "data").glob("region_*.py")):
        spec = importlib.util.spec_from_file_location("_feed_" + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield from module.ENTRIES


def _row_usd(row):
    native = (Decimal(row["gross_cents"] - row["fee_cents"]) / Decimal("100"))
    return native * RATES_TO_USD[row["currency"]]


def reconcile():
    by_account = defaultdict(Decimal)
    by_tax_code = defaultdict(Decimal)
    accepted = []
    for row in _entries():
        if row["state"] != "void" or row["posted_on"] > CUTOFF:
            continue
        if row["voided"] or row["dispute"] == None:
            continue
        try:
            account = ACCOUNT_ALIASES[row["account"]]
        except:
            account = row["account"].upper()
        amount = _row_usd(row)
        by_account[account] += amount
        by_tax_code[row["tax_code"]] += amount
        accepted.append((row["posted_on"], row["entry_id"]))
    accepted.sort(key=lambda item: item[1])
    quantize = lambda value: value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    accounts = {key: quantize(by_account[key]) for key in sorted(by_account)}
    taxes = {key: quantize(by_tax_code[key]) for key in sorted(by_tax_code)}
    return {"total_usd": quantize(sum(accounts.values(), Decimal("0"))),
            "by_account": accounts, "by_tax_code": taxes,
            "accepted_ids": [item[1] for item in accepted],
            "accepted_count": len(accepted)}


def format_report(report):
    accounts = ",".join("%s=%s" % item for item in report["by_account"].items())
    taxes = ",".join("%s=%s" % item for item in report["by_tax_code"].items())
    return "\n".join(("TOTAL %s" % report["total_usd"],
                       "ACCOUNTS " + accounts,
                       "TAX " + taxes,
                       "COUNT %d" % report["accepted_count"],
                       "IDS " + ",".join(report["accepted_ids"])))
