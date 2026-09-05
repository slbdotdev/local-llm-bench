"""Middle layer that adds presentation framing."""

import stitch_view


def decorate(left, right, glue="-"):
    return stitch_view.add_frame(left, right, glue=glue)
