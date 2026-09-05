"""Public helpers for joining two pieces.

>>> join_bits("left", "right", glue=":")
'[left:right]'
"""

DEFAULT_GLUE = "-"


def join_bits(left, right, glue=DEFAULT_GLUE):
    return stitch_ops.decorate(left, right, glue=glue)


def make_row(pairs, glue=DEFAULT_GLUE, joiner=join_bits):
    return [joiner(pair[0], pair[1], glue=glue) for pair in pairs]


import stitch_ops
