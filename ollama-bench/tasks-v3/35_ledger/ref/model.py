"""Ledger entry parsing and validation."""
import re
from collections import namedtuple
from datetime import date as _date


class LedgerError(ValueError):
    """Raised for any malformed or invalid ledger input."""


CURRENCY_SCALE = {"USD": 2, "EUR": 2, "JPY": 0, "BHD": 3}

KINDS = ("DEP", "WDR", "XFR")

Entry = namedtuple("Entry", "date kind account amount currency dest")
Entry.__new__.__defaults__ = (None,)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ACCOUNT_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_AMOUNT_RE = re.compile(r"^\d+(\.\d+)?$")


def _scale(currency):
    if currency not in CURRENCY_SCALE:
        raise LedgerError("unknown currency: %r" % (currency,))
    return CURRENCY_SCALE[currency]


def parse_amount(text, currency):
    """Parse an amount string into an integer number of minor units."""
    scale = _scale(currency)
    if not isinstance(text, str) or not _AMOUNT_RE.match(text):
        raise LedgerError("bad amount: %r" % (text,))
    whole, _, frac = text.partition(".")
    if len(frac) > scale:
        raise LedgerError("too many decimals for %s: %r" % (currency, text))
    minor = int(whole) * (10 ** scale) + int(frac.ljust(scale, "0") or "0")
    if minor <= 0:
        raise LedgerError("amount must be positive: %r" % (text,))
    return minor


def format_amount(minor, currency):
    """Render an integer number of minor units as a decimal string."""
    scale = _scale(currency)
    if scale == 0:
        return str(minor)
    sign = "-" if minor < 0 else ""
    n = abs(minor)
    return "%s%d.%0*d" % (sign, n // (10 ** scale), scale, n % (10 ** scale))


def _check_account(name):
    if not _ACCOUNT_RE.match(name):
        raise LedgerError("bad account name: %r" % (name,))
    return name


def parse_entry(line):
    """Parse one ledger line into an Entry."""
    if not isinstance(line, str):
        raise LedgerError("not a string")
    parts = [p.strip() for p in line.split("|")]
    if len(parts) not in (5, 6):
        raise LedgerError("bad field count: %d" % len(parts))
    day, kind, account, amount, currency = parts[:5]
    if not _DATE_RE.match(day):
        raise LedgerError("bad date: %r" % (day,))
    try:
        _date(int(day[0:4]), int(day[5:7]), int(day[8:10]))
    except ValueError:
        raise LedgerError("bad date: %r" % (day,))
    if kind not in KINDS:
        raise LedgerError("bad kind: %r" % (kind,))
    if kind == "XFR" and len(parts) != 6:
        raise LedgerError("XFR needs 6 fields")
    if kind != "XFR" and len(parts) != 5:
        raise LedgerError("%s needs 5 fields" % kind)
    _check_account(account)
    minor = parse_amount(amount, currency)
    dest = None
    if kind == "XFR":
        dest = _check_account(parts[5])
        if dest == account:
            raise LedgerError("transfer to self: %r" % (dest,))
    return Entry(day, kind, account, minor, currency, dest)
