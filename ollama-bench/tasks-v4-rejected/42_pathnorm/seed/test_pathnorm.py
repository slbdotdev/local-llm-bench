"""The visible examples from the task description, as runnable checks."""
from pathnorm import normalize, relative, split_root

assert normalize("a//b/./c") == "a/b/c"
assert normalize("/x/y/../z/") == "/x/z"
assert normalize("") == "."
assert normalize("C:/a/b/../c", "win") == "C:\\a\\c"
assert relative("/a/b/c", "/a/x") == "../b/c"
assert split_root("C:\\a\\b", "win") == ("C:", "\\a\\b")

print("ok")
