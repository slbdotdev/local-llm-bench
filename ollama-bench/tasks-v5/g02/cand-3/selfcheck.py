import importlib.util
import pathlib
import sys

root = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("migrate_ref", root / "ref" / "manifest_migrate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
examples = [
    ("frozen suffix", mod.migrate("title: old\n# FROZEN BELOW\nold: keep\n", {"title": "name", "old": "new"}), "name: old\n# FROZEN BELOW\nold: keep\n"),
    ("exact key", mod.migrate("old.extra: a\nold: b\n", {"old": "new"}), "old.extra: a\nnew: b\n"),
    ("comment", mod.migrate("# note old: x\n", {"old": "new"}), "# note old: x\n"),
]
for name, got, want in examples:
    print(name + ": " + ("ok" if got == want else "MISMATCH"))
    if got != want:
        sys.exit(1)
