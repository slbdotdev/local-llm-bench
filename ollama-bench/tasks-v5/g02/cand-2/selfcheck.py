import importlib.util
import pathlib
import sys

root = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("imports_ref", root / "ref" / "imports.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
examples = [
    ("from import", mod.rewrite_source("from oldpkg.widgets import Button\n", {"oldpkg": "newpkg"}), "from newpkg.widgets import Button\n"),
    ("protected string", mod.rewrite_source('# import oldpkg\nvalue = "oldpkg"\nimport oldpkg\n', {"oldpkg": "newpkg"}), '# import oldpkg\nvalue = "oldpkg"\nimport newpkg\n'),
    ("prefix boundary", mod.rewrite_source("import oldpkgx\n", {"oldpkg": "newpkg"}), "import oldpkgx\n"),
]
for name, got, want in examples:
    print(name + ": " + ("ok" if got == want else "MISMATCH"))
    if got != want:
        sys.exit(1)
