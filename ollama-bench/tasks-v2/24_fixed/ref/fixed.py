import re


class MalformedNumber(ValueError):
    pass


ROUND_HALF_EVEN = "half_even"
ROUND_HALF_UP = "half_up"
ROUND_DOWN = "down"

_GRAMMAR = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")


class Fixed:
    __slots__ = ("_units", "_scale")

    def __init__(self, s):
        if not isinstance(s, str):
            raise TypeError("Fixed() expects a str")
        if not _GRAMMAR.match(s):
            raise MalformedNumber("malformed number: %r" % (s,))
        neg = s.startswith("-")
        body = s[1:] if s[0] in "+-" else s
        parts = re.split("[eE]", body)
        mant, exp = parts[0], (int(parts[1]) if len(parts) > 1 else 0)
        ip, _, fp = mant.partition(".")
        coef = int(ip + fp)
        d = len(fp)
        if exp > d:
            units, scale = coef * 10 ** (exp - d), 0
        else:
            units, scale = coef, d - exp
        if neg:
            units = -units
        self._units = units
        self._scale = scale

    @classmethod
    def _from(cls, units, scale):
        obj = object.__new__(cls)
        obj._units = units
        obj._scale = scale
        return obj

    @staticmethod
    def _norm(units, scale):
        if units == 0:
            return (0, 0)
        while scale > 0 and units % 10 == 0:
            units //= 10
            scale -= 1
        return (units, scale)

    def __add__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        s = max(self._scale, other._scale)
        return Fixed._from(self._units * 10 ** (s - self._scale)
                           + other._units * 10 ** (s - other._scale), s)

    def __sub__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        s = max(self._scale, other._scale)
        return Fixed._from(self._units * 10 ** (s - self._scale)
                           - other._units * 10 ** (s - other._scale), s)

    def __mul__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return Fixed._from(self._units * other._units,
                           self._scale + other._scale)

    def __truediv__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        if other._units == 0:
            raise ZeroDivisionError("Fixed division by zero")
        k = 12 - self._scale + other._scale
        a, b = abs(self._units), abs(other._units)
        if k >= 0:
            n, d = a * 10 ** k, b
        else:
            n, d = a, b * 10 ** (-k)
        q, r = divmod(n, d)
        if 2 * r > d or (2 * r == d and q % 2 == 1):
            q += 1
        if (self._units < 0) != (other._units < 0):
            q = -q
        return Fixed._from(q, 12)

    def quantize(self, scale, rounding=ROUND_HALF_EVEN):
        if not isinstance(scale, int) or scale < 0:
            raise ValueError("scale must be a non-negative int")
        if rounding not in (ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_DOWN):
            raise ValueError("unknown rounding mode")
        div = 10 ** (self._scale - scale)
        if scale >= self._scale:
            return Fixed._from(self._units * 10 ** (scale - self._scale), scale)
        q, r = divmod(abs(self._units), div)
        if rounding == ROUND_DOWN:
            pass
        elif rounding == ROUND_HALF_UP:
            if 2 * r >= div:
                q += 1
        elif 2 * r > div or (2 * r == div and q % 2 == 1):
            q += 1
        units = -q if self._units < 0 else q
        return Fixed._from(units, scale)

    def __neg__(self):
        return Fixed._from(-self._units, self._scale)

    def __eq__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return (Fixed._norm(self._units, self._scale)
                == Fixed._norm(other._units, other._scale))

    def __hash__(self):
        return hash(Fixed._norm(self._units, self._scale))

    def _cmp(self, other):
        s = max(self._scale, other._scale)
        a = self._units * 10 ** (s - self._scale)
        b = other._units * 10 ** (s - other._scale)
        return (a > b) - (a < b)

    def __lt__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return self._cmp(other) < 0

    def __le__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return self._cmp(other) <= 0

    def __gt__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return self._cmp(other) > 0

    def __ge__(self, other):
        if not isinstance(other, Fixed):
            return NotImplemented
        return self._cmp(other) >= 0

    def __str__(self):
        u = self._units
        sign = "-" if u < 0 else ""
        u = abs(u)
        if self._scale == 0:
            return sign + str(u)
        ip, fp = divmod(u, 10 ** self._scale)
        return "%s%d.%0*d" % (sign, ip, self._scale, fp)

    def __repr__(self):
        return "Fixed(%r)" % str(self)
