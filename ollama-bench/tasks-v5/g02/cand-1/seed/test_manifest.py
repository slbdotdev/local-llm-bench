import unittest

import manifest


class ManifestTests(unittest.TestCase):
    def test_updates_are_case_insensitive(self):
        source = "[Deploy]\nTimeout = 30\nName = Release\n"
        expected = "[Deploy]\nTimeout = 45\nName = Release\n"
        self.assertEqual(manifest.rewrite(source, {("deploy", "timeout"): 45}), expected)

    def test_preserves_comments_and_spacing(self):
        source = "# header\n[app]\n  Port = 8080\n\n# keep\n"
        expected = "# header\n[app]\n  Port = 9000\n\n# keep\n"
        self.assertEqual(manifest.rewrite(source, {("app", "Port"): 9000}), expected)

    def test_inserts_new_key(self):
        source = "[app]\nname=demo\n"
        expected = "[app]\nname=demo\nport=80\n"
        self.assertEqual(manifest.rewrite(source, {("app", "port"): 80}), expected)

    def test_new_section(self):
        source = "[app]\nname=demo\n"
        expected = "[app]\nname=demo\n\n[worker]\nthreads=2\n"
        self.assertEqual(manifest.rewrite(source, {("worker", "threads"): 2}), expected)

    def test_values_use_last_assignment(self):
        source = "[app]\nmode=old\nmode=new\n[other]\nmode=x\n"
        self.assertEqual(manifest.values(source, "app"), {"mode": "new"})

    def test_sections_are_unique_case_insensitively(self):
        source = "[App]\nx=1\n[app]\ny=2\n[Other]\nz=3\n"
        self.assertEqual(manifest.sections(source), ["App", "Other"])

    def test_remove_is_scoped(self):
        source = "[a]\nx=1\ny=2\n[b]\nx=3\n"
        expected = "[a]\ny=2\n[b]\nx=3\n"
        self.assertEqual(manifest.remove_keys(source, [("A", "X")]), expected)


if __name__ == "__main__":
    unittest.main()
