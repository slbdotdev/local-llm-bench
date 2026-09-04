import sys, random

TOTAL = 32
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


try:
    import iniconf
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from iniconf")


P = getattr(iniconf, "parse", _missing)
Dm = getattr(iniconf, "dumps", _missing)
CE = getattr(iniconf, "ConfigError", None)


def all_raise_configerror(texts):
    def probe():
        if not (isinstance(CE, type) and issubclass(CE, BaseException)):
            return False
        for t in texts:
            try:
                P(t)
                return False
            except CE:
                pass
            except Exception:
                return False
        return True
    return probe


# --- 1: exception type -------------------------------------------------
check("ConfigError subclasses ValueError",
      lambda: isinstance(CE, type) and issubclass(CE, ValueError))

# --- 2-9: parse structure ----------------------------------------------
check("parse basic sections and keys",
      lambda: P("[a]\nx = 1\n; note\n[b]\ny = hello world\n")
      == {"a": {"x": "1"}, "b": {"y": "hello world"}})
check("parse empty and blank-only text",
      lambda: P("") == {} and P("\n\n   \n") == {})
check("parse section with no keys", lambda: P("[only]\n") == {"only": {}})
check("parse strips surrounding whitespace",
      lambda: P("  [ spaced ]  \n  k   =   v  \n") == {"spaced": {"k": "v"}})
check("parse ignores comment lines",
      lambda: P("# c\n; c\n[a]\n   # c\nk = 1\n") == {"a": {"k": "1"}}
      and P("[a]\n#[b]\nk = 1\n") == {"a": {"k": "1"}})
check("parse has no inline comments",
      lambda: P("[a]\nk = a # b\n") == {"a": {"k": "a # b"}}
      and P("[a]\nk = x;y\n") == {"a": {"k": "x;y"}})
check("parse splits on first '='",
      lambda: P("[a]\nk = v = w\n") == {"a": {"k": "v = w"}}
      and P("[a]\nk=\n") == {"a": {"k": ""}}
      and P("[a]\nk==\n") == {"a": {"k": "="}})
check("parse handles CRLF line endings",
      lambda: P("[a]\r\nx = 1\r\n[b]\r\ny = 2\r\n")
      == {"a": {"x": "1"}, "b": {"y": "2"}}
      and P("[a]\r\n\r\nx = 1") == {"a": {"x": "1"}})
check("parse handles bare CR line endings",
      lambda: P("[a]\rx = 1\r") == {"a": {"x": "1"}})

# --- 10-14: values -----------------------------------------------------
check("parse quoted values keep inner padding",
      lambda: P('[a]\np = "  padded\\t "\nq = "" \n')
      == {"a": {"p": "  padded\t ", "q": ""}})
check("parse quoted escapes \\n \\t \\\\",
      lambda: P('[a]\nk = "a\\nb"\n') == {"a": {"k": "a\nb"}}
      and P('[a]\nk = "a\\\\b"\n') == {"a": {"k": "a\\b"}})
check("parse quoted escaped quotes",
      lambda: P('[a]\nk = "he said \\"hi\\""\n') == {"a": {"k": 'he said "hi"'}}
      and P('[a]\nk = ""\n') == {"a": {"k": ""}})
check("parse unquoted values are literal",
      lambda: P('[a]\nk = a\\nb\n') == {"a": {"k": "a\\nb"}}
      and P('[a]\nk = a"b"c\n') == {"a": {"k": 'a"b"c'}})
check("parse unbalanced quotes are literal",
      lambda: P('[a]\nk = "abc\n') == {"a": {"k": '"abc'}}
      and P('[a]\nk = abc"\n') == {"a": {"k": 'abc"'}}
      and P('[a]\nk = "\n') == {"a": {"k": '"'}})

# --- 15-17: ordering ---------------------------------------------------
check("parse keeps first-appearance section order",
      lambda: list(P("[b]\nx = 1\n[a]\ny = 2\n[b]\nz = 3\n")) == ["b", "a"])
check("parse re-opens repeated sections",
      lambda: P("[b]\nx = 1\n[a]\ny = 2\n[b]\nz = 3\n")
      == {"b": {"x": "1", "z": "3"}, "a": {"y": "2"}})
check("parse keeps key insertion order",
      lambda: list(P("[s]\nc = 1\na = 2\nb = 3\n")["s"]) == ["c", "a", "b"])

# --- 18-22: errors -----------------------------------------------------
check("ConfigError on key/value before any section",
      all_raise_configerror(["x = 1\n"]))
check("ConfigError on malformed section headers",
      all_raise_configerror(["[a\nk = 1\n", "[a] x\nk = 1\n", "[]\nk = 1\n",
                             "[  ]\nk = 1\n", "[a[b]]\nk = 1\n"]))
check("ConfigError on malformed key/value lines",
      all_raise_configerror(["[a]\nnovalue\n", "[a]\n = 1\n"]))
check("ConfigError on duplicate keys",
      all_raise_configerror(["[a]\nk = 1\nk = 2\n",
                             "[a]\nk = 1\n[b]\nk = 2\n[a]\nk = 3\n"]))
check("ConfigError on bad quoted escapes",
      all_raise_configerror(['[a]\nk = "\\q"\n', '[a]\nk = "abc\\"\n',
                             '[a]\nk = "a"b"\n']))

# --- 23-28: dumps ------------------------------------------------------
check("dumps basic example",
      lambda: Dm({"s": {"a": "x", "b": " y", "c": ""}})
      == '[s]\na = x\nb = " y"\nc = ""\n')
check("dumps empty cfg and empty sections",
      lambda: Dm({}) == "" and Dm({"a": {}}) == "[a]\n"
      and Dm({"a": {}, "b": {}}) == "[a]\n\n[b]\n")
check("dumps separates sections with one blank line",
      lambda: Dm({"a": {"x": "1"}, "b": {"y": "2"}})
      == "[a]\nx = 1\n\n[b]\ny = 2\n")
check("dumps escapes control characters",
      lambda: Dm({"s": {"k": "a\nb"}}) == '[s]\nk = "a\\nb"\n'
      and Dm({"s": {"k": "a\tb"}}) == '[s]\nk = "a\\tb"\n')
check("dumps escapes backslash and quote",
      lambda: Dm({"s": {"k": "a\\b"}}) == '[s]\nk = "a\\\\b"\n'
      and Dm({"s": {"k": 'a"b'}}) == '[s]\nk = "a\\"b"\n')
check("dumps quotes padded and empty values only when needed",
      lambda: Dm({"s": {"k": "x "}}) == '[s]\nk = "x "\n'
      and Dm({"s": {"k": " x"}}) == '[s]\nk = " x"\n'
      and Dm({"s": {"k": ""}}) == '[s]\nk = ""\n')
check("dumps leaves ordinary punctuation literal",
      lambda: Dm({"s": {"k": "a # b"}}) == "[s]\nk = a # b\n"
      and Dm({"s": {"k": "a = b"}}) == "[s]\nk = a = b\n"
      and Dm({"s": {"k": "a;b"}}) == "[s]\nk = a;b\n")

# --- 29-30: round trips ------------------------------------------------


def random_round_trip():
    random.seed(7)
    alphabet = ["a", "b", " ", "\t", "\n", '"', "\\", "#", ";", "=", "1", "[", "]"]
    for _i in range(120):
        cfg = {}
        for s in range(random.randint(1, 3)):
            sec = "sec%d" % s
            cfg[sec] = {}
            for k in range(random.randint(0, 3)):
                v = "".join(random.choice(alphabet)
                            for _ in range(random.randint(0, 6)))
                cfg[sec]["k%d" % k] = v
        try:
            back = P(Dm(cfg))
        except Exception:
            return False
        if back != cfg:
            return False
    return True


check("random dumps/parse round trip", random_round_trip)
check("round trip of parsed text",
      lambda: Dm(P('[a]\nx = 1\n\n[b]\ny = " z "\n'))
      == '[a]\nx = 1\n\n[b]\ny = " z "\n')

report()
