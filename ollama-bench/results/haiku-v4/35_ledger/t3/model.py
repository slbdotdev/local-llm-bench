"""Ledger entry parsing and validation."""
import re
from collections import namedtuple
from datetime import date as _date


class LedgerError(ValueError):
    """Raised for any malformed or invalid ledger input."""


CURRENCY_SCALE = {"USD": 2, "EUR": 2, "JPY": 0, "BHD": 3}

KINDS = ("DEP", "WDR", "XFR")

# Create Entry namedtuple with default for dest field
_EntryBase = namedtuple("Entry", "date kind account amount currency dest")

class Entry(_EntryBase):
    """Entry namedtuple with dest defaulting to None for backward compatibility."""
    def __new__(cls, date, kind, account, amount, currency, dest=None):
        return super().__new__(cls, date, kind, account, amount, currency, dest)

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
    if len(parts) < 5 or len(parts) > 6:
        raise LedgerError("expected 5 or 6 fields, got %d" % len(parts))

    day, kind, account, amount, currency = parts[:5]

    if not _DATE_RE.match(day):
        raise LedgerError("bad date: %r" % (day,))
    try:
        _date(int(day[0:4]), int(day[5:7]), int(day[8:10]))
    except ValueError:
        raise LedgerError("bad date: %r" % (day,))
    if kind not in KINDS:
        raise LedgerError("bad kind: %r" % (kind,))
    _check_account(account)
    minor = parse_amount(amount, currency)

    # Handle XFR vs DEP/WDR field count
    if kind == "XFR":
        if len(parts) != 6:
            raise LedgerError("XFR requires 6 fields, got %d" % len(parts))
        dest = parts[5]
        if not dest:
            raise LedgerError("dest cannot be empty")
        _check_account(dest)
        if dest == account:
            raise LedgerError("dest cannot equal account")
        return Entry(day, kind, account, minor, currency, dest)
    else:
        if len(parts) == 6:
            raise LedgerError("%s requires 5 fields, got 6" % kind)
        return Entry(day, kind, account, minor, currency, None)
