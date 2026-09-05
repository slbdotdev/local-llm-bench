import doctest

import stitch_base
import stitch_view


def test_suite():
    assert doctest.testmod(stitch_base).failed == 0
    assert stitch_base.merge_bits("b", "a", glue=":") == "[a:b]"
    assert stitch_base.make_row([("a", "b"), ("c", "d")]) == ["[a-b]", "[c-d]"]
    assert stitch_view.reflected(("x", "y"), glue="/") == "[y/x]"


if __name__ == "__main__":
    test_suite()
