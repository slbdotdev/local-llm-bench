import unittest

import imports


class ImportRewriteTests(unittest.TestCase):
    def test_from_import_is_rewritten(self):
        source = "from oldpkg.widgets import Button\n"
        expected = "from newpkg.widgets import Button\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_plain_import_is_rewritten(self):
        source = "import oldpkg.tools as tools\n"
        expected = "import newpkg.tools as tools\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_strings_and_comments_are_untouched(self):
        source = '# import oldpkg\nmessage = "import oldpkg"\nimport oldpkg\n'
        expected = '# import oldpkg\nmessage = "import oldpkg"\nimport newpkg\n'
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_prefix_boundary(self):
        source = "import oldpkgx\nimport oldpkg.extra\n"
        expected = "import oldpkgx\nimport newpkg.extra\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_multiple_imports(self):
        source = "import oldpkg.a, other, oldpkg.b\n"
        expected = "import newpkg.a, other, newpkg.b\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_multiline_plain_import(self):
        source = "import oldpkg.sub as sub\n"
        expected = "import newpkg.sub as sub\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), expected)

    def test_relative_import_is_untouched(self):
        source = "from .oldpkg import value\n"
        self.assertEqual(imports.rewrite_source(source, {"oldpkg": "newpkg"}), source)

    def test_imported_modules(self):
        source = "import one.two\nimport three, four.five\n"
        self.assertEqual(imports.imported_modules(source), ["one.two", "three", "four.five"])


if __name__ == "__main__":
    unittest.main()
