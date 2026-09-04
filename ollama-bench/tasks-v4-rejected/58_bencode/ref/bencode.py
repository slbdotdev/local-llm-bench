"""Strict canonical bencode codec."""

DEPTH_LIMIT = 32
INT_MIN = -(2 ** 63)
INT_MAX = 2 ** 63 - 1
MAX_LEN = 2 ** 31 - 1


class BencodeError(Exception):
    def __init__(self, kind, offset=None):
        Exception.__init__(self, "%s at %r" % (kind, offset))
        self.kind = kind
        self.offset = offset


# ---------------------------------------------------------------- encode

def encode(obj):
    out = []
    _enc(obj, 1, out)
    return b"".join(out)


def _enc(o, depth, out):
    t = type(o)
    if t is bool:
        raise BencodeError("bool")
    if t is int:
        if o < INT_MIN or o > INT_MAX:
            raise BencodeError("range")
        out.append(b"i" + str(o).encode("ascii") + b"e")
        return
    if t is bytes:
        out.append(str(len(o)).encode("ascii") + b":" + o)
        return
    if t is list:
        if depth > DEPTH_LIMIT:
            raise BencodeError("depth")
        out.append(b"l")
        for x in o:
            _enc(x, depth + 1, out)
        out.append(b"e")
        return
    if t is dict:
        if depth > DEPTH_LIMIT:
            raise BencodeError("depth")
        for k in o:
            if type(k) is not bytes:
                raise BencodeError("key_type")
        out.append(b"d")
        for k in sorted(o):
            out.append(str(len(k)).encode("ascii") + b":" + k)
            _enc(o[k], depth + 1, out)
        out.append(b"e")
        return
    raise BencodeError("type")


# ---------------------------------------------------------------- decode

def decode(data):
    if type(data) is not bytes:
        raise BencodeError("type", 0)
    obj, j = _dec(data, 0, 1)
    if j != len(data):
        raise BencodeError("trailing", j)
    return obj


def _dec(d, i, depth):
    n = len(d)
    if i >= n:
        raise BencodeError("truncated", n)
    c = d[i]
    if c == 0x69:                      # 'i'
        j = d.find(b"e", i + 1)
        if j < 0:
            raise BencodeError("truncated", n)
        neg = (i + 1 < j and d[i + 1] == 0x2D)
        k = i + 2 if neg else i + 1
        if k >= j:
            raise BencodeError("syntax", k)
        for p in range(k, j):
            if not (0x30 <= d[p] <= 0x39):
                raise BencodeError("syntax", p)
        if j - k > 1 and d[k] == 0x30:
            raise BencodeError("leading_zero", k)
        if neg and d[k] == 0x30:
            raise BencodeError("negative_zero", i + 1)
        if j - k > 19:
            raise BencodeError("range", i)
        v = int(d[i + 1:j])
        if v < INT_MIN or v > INT_MAX:
            raise BencodeError("range", i)
        return v, j + 1
    if 0x30 <= c <= 0x39:              # byte string
        j = d.find(b":", i)
        if j < 0:
            raise BencodeError("truncated", n)
        for p in range(i, j):
            if not (0x30 <= d[p] <= 0x39):
                raise BencodeError("syntax", p)
        if j - i > 1 and d[i] == 0x30:
            raise BencodeError("leading_zero", i)
        if j - i > 10:
            raise BencodeError("range", i)
        L = int(d[i:j])
        if L > MAX_LEN:
            raise BencodeError("range", i)
        e = j + 1 + L
        if e > n:
            raise BencodeError("truncated", n)
        return d[j + 1:e], e
    if c == 0x6C:                      # 'l'
        if depth > DEPTH_LIMIT:
            raise BencodeError("depth", i)
        out = []
        p = i + 1
        while True:
            if p >= n:
                raise BencodeError("truncated", n)
            if d[p] == 0x65:
                return out, p + 1
            v, p = _dec(d, p, depth + 1)
            out.append(v)
    if c == 0x64:                      # 'd'
        if depth > DEPTH_LIMIT:
            raise BencodeError("depth", i)
        res = {}
        prev = None
        p = i + 1
        while True:
            if p >= n:
                raise BencodeError("truncated", n)
            b = d[p]
            if b == 0x65:
                return res, p + 1
            if b == 0x69 or b == 0x6C or b == 0x64:
                raise BencodeError("key_type", p)
            if not (0x30 <= b <= 0x39):
                raise BencodeError("syntax", p)
            key, p2 = _dec(d, p, depth + 1)
            if prev is not None:
                if key == prev:
                    raise BencodeError("duplicate_key", p)
                if key < prev:
                    raise BencodeError("key_order", p)
            prev = key
            val, p = _dec(d, p2, depth + 1)
            res[key] = val
    raise BencodeError("syntax", i)
