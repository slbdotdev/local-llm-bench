from sedlite import run, ScriptError

assert run("s/a/X/", "abca\nxyz\n") == "Xbca\nxyz\n"
assert run("2d", "one\ntwo\nthree\n") == "one\nthree\n"
assert run("/b/p", "a\nb\n", quiet=True) == "b\n"
assert run("1a hello", "x\ny\n") == "x\nhello\ny\n"
assert run("s,o,0,g", "foo boo\n") == "f00 b00\n"

print("ok")
