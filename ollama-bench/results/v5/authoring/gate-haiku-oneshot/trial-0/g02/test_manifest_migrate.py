import unittest

import manifest_migrate


class MigrationTests(unittest.TestCase):
    def test_frozen_tail_is_not_changed(self):
        source = "title: old\n# FROZEN BELOW\nold: keep-this\n"
        expected = "new: old\n# FROZEN BELOW\nold: keep-this\n"
        self.assertEqual(manifest_migrate.migrate(source, {"title": "new", "old": "new"}), expected)

    def test_editable_keys_change(self):
        source = "old: one\nother: two\n"
        expected = "new: one\nother: two\n"
        self.assertEqual(manifest_migrate.migrate(source, {"old": "new"}), expected)

    def test_values_are_not_changed(self):
        source = "title: old\n"
        self.assertEqual(manifest_migrate.migrate(source, {"title": "name", "old": "new"}), "name: old\n")

    def test_comments_and_blank_lines_stay(self):
        source = "# old: comment\n\nold: value  # old\n"
        expected = "# old: comment\n\nnew: value  # old\n"
        self.assertEqual(manifest_migrate.migrate(source, {"old": "new"}), expected)

    def test_exact_key_matching(self):
        source = "old.extra: a\nold: b\n"
        expected = "old.extra: a\nnew: b\n"
        self.assertEqual(manifest_migrate.migrate(source, {"old": "new"}), expected)

    def test_keys_can_exclude_tail(self):
        source = "a: 1\n# FROZEN BELOW\nb: 2\n"
        self.assertEqual(manifest_migrate.keys(source, False), ["a"])
        self.assertEqual(manifest_migrate.keys(source), ["a", "b"])

    def test_count_defaults_to_editable_part(self):
        source = "a: 1\na: 2\n# FROZEN BELOW\na: 3\n"
        self.assertEqual(manifest_migrate.migration_count(source, {"a": "z"}), 2)
        self.assertEqual(manifest_migrate.migration_count(source, {"a": "z"}, True), 3)

    def test_tail_comparison(self):
        source = "a: 1\n# FROZEN BELOW\na: 2\n"
        output = "a: z\n# FROZEN BELOW\na: 2\n"
        self.assertTrue(manifest_migrate.unchanged_tail(source, output))


if __name__ == "__main__":
    unittest.main()
