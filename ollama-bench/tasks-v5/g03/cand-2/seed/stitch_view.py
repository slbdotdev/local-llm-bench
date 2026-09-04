"""View and reflective entry points."""

import stitch_base


def add_frame(left, right, glue="-"):
    return "[%s]" % (left + glue + right)


def _fallback(right, left, glue="-"):
    return add_frame(left, right, glue=glue)


def reflected(pair, glue="-"):
    joiner = getattr(stitch_base, "join_bits", _fallback)
    return joiner(pair[1], pair[0], glue=glue)
