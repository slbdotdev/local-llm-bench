"""Exact money arithmetic on decimal strings, using integer arithmetic only."""
import re

ROUND_HALF_EVEN = "half_even"
ROUND_HALF_UP = "half_up"
ROUND_HALF_DOWN = "half_down"
ROUND_CEILING = "ceiling"
ROUND_FLOOR = "floor"
ROUND_DOWN = "down"
ROUND_UP = "up"

_MODES = frozenset([ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_HALF_DOWN,
                    ROUND_CEILING, ROUND_FLOOR, ROUND_DOWN, ROUND_UP])

_NUM = re.compile(r"^[+-]?[0-9]+(\.[0-9]+)?$")


class MoneyError(ValueError):
    pass


def _parse(s):
    """Return (units, dec) with exact value == units / 10**dec."""
    if not isinstance(s, str) or _NUM.match(s) is None:
        raise MoneyError("malformed amount: %r" % (s,))
    neg = s[0] == "-"
    if s[0] in "+-":
        s = s[1:]
    if "." in s:
        head, tail = s.split(".")
    else:
        head, tail = s, ""
    units = int(head + tail) if (head + tail) else 0
    if neg:
        units = -units
    return units, len(tail)


def _check_places(places):
    if not isinstance(places, int) or places < 0:
        raise MoneyError("bad places: %r" % (places,))


def _check_mode(mode):
    if mode not in _MODES:
        raise MoneyError("bad rounding mode: %r" % (mode,))


def _round(num, den, places, mode):
    """Round the exact rational num/den (den > 0) to an integer count of 10**-places."""
    n = num * (10 ** places)
    q = n // den
    r = n - den * q
    if r == 0:
        return q
    if mode == ROUND_FLOOR:
        return q
    if mode == ROUND_CEILING:
        return q + 1
    below_zero = n < 0
    if mode == ROUND_DOWN:
        return q + 1 if below_zero else q
    if mode == ROUND_UP:
        return q if below_zero else q + 1
    twice = 2 * r
    if twice > den:
        return q + 1
    if twice < den:
        return q
    if mode == ROUND_HALF_UP:
        return q if below_zero else q + 1
    if mode == ROUND_HALF_DOWN:
        return q + 1 if below_zero else q
    return q if q % 2 == 0 else q + 1


def _fmt(units, places):
    sign = "-" if units < 0 else ""
    body = str(abs(units))
    if places:
        if len(body) <= places:
            body = "0" * (places + 1 - len(body)) + body
        body = body[:-places] + "." + body[-places:]
    return sign + body


def _exact_units(text, places, what):
    """Parse an amount that must be exactly representable at `places`."""
    units, dec = _parse(text)
    if dec > places:
        raise MoneyError("%s is not representable at %d places" % (what, places))
    return units * (10 ** (places - dec))


def quantize(amount, places, mode):
    _check_places(places)
    _check_mode(mode)
    units, dec = _parse(amount)
    return _fmt(_round(units, 10 ** dec, places, mode), places)


def allocate(total, weights, places):
    _check_places(places)
    if not isinstance(weights, (list, tuple)):
        raise MoneyError("weights must be a list")
    parsed = [_parse(w) for w in weights]
    for units, _dec in parsed:
        if units < 0:
            raise MoneyError("negative weight")
    T = _exact_units(total, places, "total")
    n = len(parsed)
    if n == 0:
        if T != 0:
            raise MoneyError("cannot allocate a non-zero total to no shares")
        return []
    k = max(dec for _u, dec in parsed)
    w = [u * (10 ** (k - dec)) for u, dec in parsed]
    S = sum(w)
    if S == 0:
        w = [1] * n
        S = n
    shares = []
    rems = []
    for i in range(n):
        prod = T * w[i]
        q = prod // S
        shares.append(q)
        rems.append(prod - S * q)
    left = T - sum(shares)
    order = sorted(range(n), key=lambda i: (-rems[i], i))
    for i in order[:left]:
        shares[i] += 1
    return [_fmt(v, places) for v in shares]


def _rate_parts(rate):
    units, dec = _parse(rate)
    if units < 0:
        raise MoneyError("negative rate")
    return units, dec


def add_tax(net, rate, places, mode):
    _check_places(places)
    _check_mode(mode)
    ru, rd = _rate_parts(rate)
    nu, nd = _parse(net)
    if nd > places:
        raise MoneyError("net is not representable at %d places" % places)
    net_units = nu * (10 ** (places - nd))
    # exact tax = (nu / 10**nd) * (ru / 10**rd) / 100
    tax_units = _round(nu * ru, 10 ** (nd + rd + 2), places, mode)
    return (_fmt(net_units, places), _fmt(tax_units, places),
            _fmt(net_units + tax_units, places))


def extract_tax(gross, rate, places, mode):
    _check_places(places)
    _check_mode(mode)
    ru, rd = _rate_parts(rate)
    gu, gd = _parse(gross)
    if gd > places:
        raise MoneyError("gross is not representable at %d places" % places)
    gross_units = gu * (10 ** (places - gd))
    # exact tax = gross * rate / (100 + rate)
    #           = (gu * ru) / (10**gd * (100 * 10**rd + ru))
    den = (10 ** gd) * (100 * (10 ** rd) + ru)
    tax_units = _round(gu * ru, den, places, mode)
    return (_fmt(gross_units - tax_units, places), _fmt(tax_units, places),
            _fmt(gross_units, places))
