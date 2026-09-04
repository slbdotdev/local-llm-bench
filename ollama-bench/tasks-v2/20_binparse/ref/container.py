"""Reference implementation of the BINP container format."""
import zlib

MAGIC = b"BINP"
VERSION = 2


class ContainerError(Exception):
    pass


class BadMagicError(ContainerError):
    pass


class UnsupportedVersionError(ContainerError):
    pass


class TruncatedError(ContainerError):
    pass


class ChecksumError(ContainerError):
    pass


class LengthError(ContainerError):
    pass


class InvalidUTF8Error(ContainerError):
    pass


class TrailingDataError(ContainerError):
    pass


def _be32(n):
    return n.to_bytes(4, "big")


def _enc_str(s):
    b = s.encode("utf-8")
    return _be32(len(b)) + b


def pack(obj):
    out = MAGIC + bytes([obj["version"]]) + _be32(len(obj["records"]))
    for r in obj["records"]:
        flags = (1 if "score" in r else 0) | (2 if "tag" in r else 0)
        out += bytes([flags]) + _be32(r["id"])
        out += _enc_str(r["name"])
        if "score" in r:
            out += _be32(r["score"])
        if "tag" in r:
            out += _enc_str(r["tag"])
    return out + zlib.crc32(out).to_bytes(4, "big")


def parse(data):
    if len(data) < 13:
        raise TruncatedError("container too short")
    if data[:4] != MAGIC:
        raise BadMagicError("bad magic")
    if data[4] != VERSION:
        raise UnsupportedVersionError("unsupported version")
    body, stored = data[:-4], data[-4:]
    if zlib.crc32(body) != int.from_bytes(stored, "big"):
        raise ChecksumError("checksum mismatch")
    count = int.from_bytes(data[5:9], "big")
    pos = 9
    end = len(data) - 4
    records = []
    for _ in range(count):
        if pos + 5 > end:
            raise TruncatedError("truncated record header")
        flags = data[pos]
        pos += 1
        rec = {"id": int.from_bytes(data[pos:pos + 4], "big")}
        pos += 4
        if pos + 4 > end:
            raise TruncatedError("truncated name length")
        nlen = int.from_bytes(data[pos:pos + 4], "big")
        pos += 4
        if nlen > end - pos:
            raise LengthError("name length exceeds remaining data")
        try:
            rec["name"] = data[pos:pos + nlen].decode("utf-8")
        except UnicodeDecodeError:
            raise InvalidUTF8Error("invalid utf-8 in name")
        pos += nlen
        if flags & 1:
            if pos + 4 > end:
                raise TruncatedError("truncated score")
            rec["score"] = int.from_bytes(data[pos:pos + 4], "big")
            pos += 4
        if flags & 2:
            if pos + 4 > end:
                raise TruncatedError("truncated tag length")
            tlen = int.from_bytes(data[pos:pos + 4], "big")
            pos += 4
            if tlen > end - pos:
                raise LengthError("tag length exceeds remaining data")
            try:
                rec["tag"] = data[pos:pos + tlen].decode("utf-8")
            except UnicodeDecodeError:
                raise InvalidUTF8Error("invalid utf-8 in tag")
            pos += tlen
        records.append(rec)
    if pos != end:
        raise TrailingDataError("trailing bytes before checksum")
    return {"version": data[4], "records": records}
