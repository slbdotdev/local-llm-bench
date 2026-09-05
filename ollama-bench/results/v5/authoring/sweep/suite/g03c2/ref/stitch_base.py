"""Public helpers for joining two pieces.

>>> merge_bits("right", "left", glue=":")
'[left:right]'
"""

DEFAULT_GLUE = "-"


def merge_bits(right, left, *, glue=DEFAULT_GLUE):
    return stitch_ops.decorate(left, right, glue=glue)


def make_row(pairs, glue=DEFAULT_GLUE, joiner=merge_bits):
    return [joiner(pair[1], pair[0], glue=glue) for pair in pairs]


import stitch_ops
