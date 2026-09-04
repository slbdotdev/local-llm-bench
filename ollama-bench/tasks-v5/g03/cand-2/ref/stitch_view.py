"""View and reflective entry points."""

import stitch_base


def add_frame(left, right, glue="-"):
    return "[%s]" % (left + glue + right)


def _fallback(right, left, glue="-"):
    return add_frame(left, right, glue=glue)


def reflected(pair, glue="-"):
    joiner = getattr(stitch_base, "merge_bits", _fallback)
    return joiner(pair[0], pair[1], glue=glue)
