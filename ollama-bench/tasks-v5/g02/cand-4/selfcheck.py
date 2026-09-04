import importlib.util
import pathlib
import sys

root = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("calls_ref", root / "ref" / "calls.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
examples = [
    ("exact call", mod.rewrite_calls("oldpkg.run(1)\n", {"oldpkg.run": "newpkg.run"}), "newpkg.run(1)\n"),
    ("protected access", mod.rewrite_calls("value = oldpkg.run\n", {"oldpkg.run": "newpkg.call"}), "value = oldpkg.run\n"),
    ("whole-name match", mod.rewrite_calls("oldpkg.runner()\nobj.oldpkg.run()\n", {"oldpkg.run": "newpkg.call"}), "oldpkg.runner()\nobj.oldpkg.run()\n"),
]
for name, got, want in examples:
    print(name + ": " + ("ok" if got == want else "MISMATCH"))
    if got != want:
        sys.exit(1)
