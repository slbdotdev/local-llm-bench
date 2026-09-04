import os
import sys
import threading


TOTAL = 24
fails = []
done = 0
_lock = threading.Lock()
_visible_failure = False


def _ora_word(ch):
    return ("a" <= ch <= "z" or "A" <= ch <= "Z" or
            "0" <= ch <= "9" or ch == "_")


def _ora_transform(text):
    out = []
    i = 0
    count = 0
    while i < len(text):
        if text[i] == "#" and (i == 0 or text[i - 1] == " "):
            out.append(text[i:])
            break
        if "0" <= text[i] <= "9":
            start = i
            while i < len(text) and "0" <= text[i] <= "9":
                i += 1
            eligible = ((start == 0 or not _ora_word(text[start - 1])) and
                        (i == len(text) or not _ora_word(text[i])))
            if eligible and count < 3:
                out.extend(("<", text[start:i], ">"))
                count += 1
            else:
                out.append(text[start:i])
            if count == 3:
                out.append(text[i:])
                break
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _check(name, fn):
    global done, _visible_failure
    try:
        ok = bool(fn())
    except Exception:
        ok = False
        _visible_failure = True
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def _watchdog():
    with _lock:
        n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _watchdog)
_timer.daemon = True
_timer.start()


def _report(module, import_failed=False):
    _timer.cancel()
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        if import_failed or _visible_failure:
            verdict = "visibly_failed"
        else:
            verdict = "confidently_wrong"
        print("VERDICT " + verdict)
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


try:
    import solution as _candidate
    _transform = getattr(_candidate, "transform")
    if not callable(_transform):
        raise TypeError("transform is not callable")
except Exception as _error:
    fails = ["load solution"] + ["not run"] * (TOTAL - 1)
    _report(None, import_failed=True)


_cases = [
    ("empty", "", ""),
    ("plain text", "nothing to change", "nothing to change"),
    ("one run", "item 12", "item <12>"),
    ("two runs", "ID 12, cost=7", "ID <12>, cost=<7>"),
    ("three runs", "one 1 two 22 three 333", "one <1> two <22> three <333>"),
    ("fourth preserved", "one 1 two 22 three 333 four 444",
     "one <1> two <22> three <333> four 444"),
    ("start boundary", "0 at start", "<0> at start"),
    ("end boundary", "at end 9", "at end <9>"),
    ("punctuation", "[12] (34)! 56?", "[<12>] (<34>)! <56>?"),
    ("ascii letter left", "x12 34", "x12 <34>"),
    ("ascii letter right", "12x 34", "12x <34>"),
    ("underscore left", "a_12 34", "a_12 <34>"),
    ("underscore right", "12_34 56", "12_34 <56>"),
    ("split underscore", "123_456", "123_456"),
    ("unicode left is open", "é123", "é<123>"),
    ("unicode right is open", "123é", "<123>é"),
    ("comment after space", "count 1 # keep 2 and 3",
     "count <1> # keep 2 and 3"),
    ("comment at start", "# 1 2 3", "# 1 2 3"),
    ("hash after tab", "count 1\t# not a comment 2",
     "count <1>\t# not a comment <2>"),
    ("hash after letter", "abc# 12 34", "abc# <12> <34>"),
    ("hash after two spaces", "x  # 12 34", "x  # 12 34"),
    ("newlines preserved", "a\n12\n\t34", "a\n<12>\n\t<34>"),
    ("empty digit fields", "  0..9  ", "  <0>..<9>  "),
    ("blocked runs do not count", "a12 34_ 56 78", "a12 34_ <56> <78>"),
]


for _name, _source, _expected in _cases:
    def _run_case(s=_source, e=_expected):
        global _visible_failure
        try:
            actual = _transform(s)
        except Exception:
            _visible_failure = True
            return False
        if not isinstance(actual, str):
            _visible_failure = True
            return False
        return actual == e

    _check(_name, _run_case)

_report(_candidate)
