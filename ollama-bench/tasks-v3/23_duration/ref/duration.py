import re


def format_duration(total_seconds: int) -> str:
    d, rem = divmod(total_seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s:
        parts.append(f"{s}s")
    if not parts:
        return "0s"
    return "".join(parts)


_D = r"([1-9]\d*)d"
_H = r"([1-9]|1\d|2[0-3])h"
_M = r"([1-9]|[1-5]\d)m"
_S = r"([1-9]|[1-5]\d)s"
_PATTERN = re.compile(f"^(?:{_D})?(?:{_H})?(?:{_M})?(?:{_S})?$")


def parse_duration(s: str) -> int:
    if s == "0s":
        return 0
    m = _PATTERN.fullmatch(s) if s else None
    if not m:
        raise ValueError(f"invalid duration: {s!r}")
    d, h, mi, se = m.groups()
    if not any([d, h, mi, se]):
        raise ValueError(f"invalid duration: {s!r}")
    total = 0
    if d:
        total += int(d) * 86400
    if h:
        total += int(h) * 3600
    if mi:
        total += int(mi) * 60
    if se:
        total += int(se)
    return total
