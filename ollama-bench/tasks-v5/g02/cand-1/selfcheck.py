import importlib.util
import pathlib
import sys

root = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("manifest_ref", root / "ref" / "manifest.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
examples = [
    ("case-insensitive update", mod.rewrite("[Deploy]\nTimeout = 30\n", {("deploy", "timeout"): 45}), "[Deploy]\nTimeout = 45\n"),
    ("missing key insertion", mod.rewrite("[app]\nname=demo\n", {("app", "port"): 80}), "[app]\nname=demo\nport=80\n"),
    ("scoped removal", mod.remove_keys("[a]\nx=1\ny=2\n[b]\nx=3\n", [("A", "X")]), "[a]\ny=2\n[b]\nx=3\n"),
]
for name, got, want in examples:
    print(name + ": " + ("ok" if got == want else "MISMATCH"))
    if got != want:
        sys.exit(1)
