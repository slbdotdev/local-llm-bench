import unittest

import calls


class CallRewriteTests(unittest.TestCase):
    def test_rewrites_exact_call_targets(self):
        source = ("oldpkg.run(1)\n"
                  "result = oldpkg.run (2)\n"
                  "other(oldpkg.run(3), oldpkg.stop())\n")
        expected = ("newpkg.call(1)\n"
                    "result = newpkg.call (2)\n"
                    "other(newpkg.call(3), oldpkg.stop())\n")
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg.run": "newpkg.call"}), expected)

    def test_attribute_use_is_not_a_call(self):
        source = "value = oldpkg.run\ntext = 'oldpkg.run()'\n"
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg.run": "newpkg.call"}), source)

    def test_no_prefix_or_subexpression_match(self):
        source = "oldpkg.runner()\noldpkg.run.extra()\nobj.oldpkg.run()\n"
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg.run": "newpkg.call"}), source)

    def test_comments_are_not_calls(self):
        source = "# oldpkg.run()\nvalue = 'oldpkg.run()'\n"
        expected = source
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg.run": "newpkg.call"}), expected)

    def test_newline_ends_call_expression(self):
        source = "oldpkg.run\n()\n"
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg.run": "newpkg.call"}), source)

    def test_definitions_are_not_calls(self):
        source = "def oldpkg():\n    return 1\nclass oldpkg():\n    pass\n"
        self.assertEqual(calls.rewrite_calls(
            source, {"oldpkg": "newpkg"}), source)

    def test_called_names_are_maximal_and_ordered(self):
        source = "outer(oldpkg.run(), obj.done())\noldpkg.stop()\n"
        self.assertEqual(calls.called_names(source),
                         ["outer", "oldpkg.run", "obj.done", "oldpkg.stop"])

    def test_call_count_exact_match(self):
        source = "oldpkg.run()\noldpkg.runner()\noldpkg.run()\n"
        self.assertEqual(calls.call_count(source), 3)
        self.assertEqual(calls.call_count(source, "oldpkg.run"), 2)


if __name__ == "__main__":
    unittest.main()
