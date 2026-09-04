import sys, os, io, csv, random, threading, inspect

TOTAL = 25
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()

try:
    import csvfmt
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

_CE = getattr(csvfmt, "CsvError", None)
if not (isinstance(_CE, type) and issubclass(_CE, BaseException)):
    _CE = None

_ora_BS = chr(92)
_ora_QMAP = {"minimal": csv.QUOTE_MINIMAL, "all": csv.QUOTE_ALL,
             "nonnumeric": csv.QUOTE_NONNUMERIC, "none": csv.QUOTE_NONE}
_ora_DELIMS = [",", ";", "|", "\t"]
_ora_QUOTES = ['"', "'"]
_ora_ESCS = [None, _ora_BS, "!"]
_ora_LTS = ["\r\n", "\n"]


def _ora_write(fields, d):
    dd = dict(d)
    dd["quoting"] = _ora_QMAP[dd["quoting"]]
    dd.pop("skipinitialspace", None)
    s = io.StringIO()
    try:
        csv.writer(s, **dd).writerow(list(fields))
    except (csv.Error, ValueError):
        return ("ERR",)
    return s.getvalue()


def _ora_read(text, d):
    dd = dict(d)
    dd["quoting"] = _ora_QMAP[dd["quoting"]]
    dd.pop("lineterminator", None)
    try:
        return [list(r) for r in csv.reader(io.StringIO(text, newline=""), **dd)]
    except (csv.Error, ValueError):
        return ("ERR",)


def _ora_cand_write(fields, d):
    try:
        return csvfmt.write_row(list(fields), **d)
    except Exception as e:
        if _CE is not None and isinstance(e, _CE):
            return ("ERR",)
        return ("BADEXC", type(e).__name__)


def _ora_cand_read(text, d):
    try:
        return csvfmt.read_rows(text, **d)
    except Exception as e:
        if _CE is not None and isinstance(e, _CE):
            return ("ERR",)
        return ("BADEXC", type(e).__name__)


def _ora_dialect(rng, quotings=None, escs=None, dqs=None, sis=None):
    while True:
        d = dict(delimiter=rng.choice(_ora_DELIMS),
                 quotechar=rng.choice(_ora_QUOTES),
                 escapechar=rng.choice(_ora_ESCS if escs is None else escs),
                 doublequote=rng.choice([True, False] if dqs is None else dqs),
                 quoting=rng.choice(quotings or
                                    ["minimal", "all", "nonnumeric", "none"]),
                 lineterminator=rng.choice(_ora_LTS),
                 skipinitialspace=rng.choice([False, True] if sis is None
                                             else sis))
        chs = [d["delimiter"], d["quotechar"]]
        if d["escapechar"] is not None:
            chs.append(d["escapechar"])
        if len(set(chs)) == len(chs):
            return d


_ora_CH = ["a", "b", "Z", "e", "0", "1", "2", ".", "-", " ", " ", ",", ";",
           "|", "\t", '"', "'", _ora_BS, "!", "\r", "\n"]


def _ora_field(rng, maxlen=8):
    return "".join(rng.choice(_ora_CH) for _ in range(rng.randint(0, maxlen)))


def _ora_fields(rng, d, numeric=False):
    out = []
    for _ in range(rng.randint(0, 5)):
        if numeric and rng.random() < 0.4:
            out.append(rng.choice([0, 1, -7, 13, 2.5, -0.5, 42.0, 100]))
        else:
            out.append(_ora_field(rng))
    return out


_ora_BASE = ["a", "b", "Z", "e", "0", "1", "2", ".", "-", " ", " "]


def _ora_alpha(d):
    al = list(_ora_BASE)
    al += [d["delimiter"]] * 3 + [d["quotechar"]] * 4 + ["\r", "\n"]
    if d["escapechar"] is not None:
        al += [d["escapechar"]] * 3
    return al


def _ora_text(rng, d=None, maxlen=24):
    al = _ora_CH if d is None else _ora_alpha(d)
    return "".join(rng.choice(al) for _ in range(rng.randint(0, maxlen)))


def _ora_wprobe(cases):
    def probe():
        for fields, d in cases:
            if _ora_write(fields, d) != _ora_cand_write(fields, d):
                return False
        return True
    return probe


def _ora_rprobe(cases):
    def probe():
        for text, d in cases:
            if _ora_read(text, d) != _ora_cand_read(text, d):
                return False
        return True
    return probe


def _ora_split(cases, k):
    n = len(cases)
    return [cases[i * n // k:(i + 1) * n // k] for i in range(k)]


# --- 1: no csv import --------------------------------------------------
def _ora_no_csv():
    try:
        src = inspect.getsource(csvfmt)
    except Exception:
        return False
    import re as _ora_re
    pat = r"^\s*(import|from)\s+(_?csv|pandas)\b"
    return _ora_re.search(pat, src, _ora_re.M) is None


check("csvfmt does not import csv/_csv/pandas", _ora_no_csv)

# --- 2: exception type -------------------------------------------------
check("CsvError subclasses ValueError",
      lambda: isinstance(getattr(csvfmt, "CsvError", None), type)
      and issubclass(csvfmt.CsvError, ValueError))

# --- 3: the visible examples -------------------------------------------
check("visible examples",
      lambda: csvfmt.write_row(["a", "b,c", 'say "hi"', ""])
      == 'a,"b,c","say ""hi""",\r\n'
      and csvfmt.write_row(["x"], quoting="all", lineterminator="\n") == '"x"\n'
      and csvfmt.write_row(["a", "b"], delimiter=";") == "a;b\r\n"
      and csvfmt.read_rows('a,"b,c"\r\nd,"e\nf"\r\n')
      == [["a", "b,c"], ["d", "e\nf"]]
      and csvfmt.read_rows("a;b\n\nc;\n", delimiter=";")
      == [["a", "b"], [], ["c", ""]])

# --- 4-5: write, simple dialects (minimal / all, no escapechar) --------
_r = random.Random(4041)
_cases = []
for _i in range(300):
    _d = _ora_dialect(_r, quotings=["minimal", "all"], escs=[None], dqs=[True])
    _cases.append((_ora_fields(_r, _d), _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("write: minimal/all dialects, part %d" % (_k + 1), _ora_wprobe(_part))

# --- 6-8: write, the whole option space --------------------------------
_r = random.Random(4042)
_cases = []
for _i in range(600):
    _d = _ora_dialect(_r)
    _cases.append((_ora_fields(_r, _d, numeric=True), _d))
for _k, _part in enumerate(_ora_split(_cases, 3)):
    check("write: full dialect space, part %d" % (_k + 1), _ora_wprobe(_part))

# --- 9-10: write, cases where the reference raises ---------------------
_r = random.Random(4043)
_cases = []
while len(_cases) < 240:
    _d = _ora_dialect(_r, escs=[None])
    _f = _ora_fields(_r, _d)
    if _ora_write(_f, _d) == ("ERR",):
        _cases.append((_f, _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("write: CsvError cases, part %d" % (_k + 1), _ora_wprobe(_part))

# --- 11: write, nonnumeric with int/float values -----------------------
_r = random.Random(4044)
_cases = []
for _i in range(260):
    _d = _ora_dialect(_r, quotings=["nonnumeric"])
    _cases.append((_ora_fields(_r, _d, numeric=True), _d))
check("write: nonnumeric with int/float values", _ora_wprobe(_cases))

# --- 12-13: read text produced by the reference writer -----------------
_r = random.Random(4045)
_cases = []
while len(_cases) < 400:
    _d = _ora_dialect(_r)
    _parts = []
    for _j in range(_r.randint(1, 3)):
        _w = _ora_write(_ora_fields(_r, _d, numeric=True), _d)
        if isinstance(_w, tuple):
            _parts = None
            break
        _parts.append(_w)
    if _parts:
        _cases.append(("".join(_parts), _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("read: well-formed multi-record text, part %d" % (_k + 1),
          _ora_rprobe(_part))

# --- 14-15: read arbitrary text, minimal / all -------------------------
_r = random.Random(4046)
_cases = []
for _i in range(400):
    _d = _ora_dialect(_r, quotings=["minimal", "all"], escs=[None], dqs=[True],
                      sis=[False])
    _cases.append((_ora_text(_r, _d), _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("read: arbitrary text, minimal/all, part %d" % (_k + 1),
          _ora_rprobe(_part))

# --- 16-17: read arbitrary text with an escapechar ---------------------
_r = random.Random(4047)
_cases = []
for _i in range(400):
    _d = _ora_dialect(_r, quotings=["minimal", "all"],
                      escs=[_ora_BS, "!"], dqs=[True], sis=[False])
    _cases.append((_ora_text(_r, _d), _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("read: arbitrary text with escapechar, part %d" % (_k + 1),
          _ora_rprobe(_part))

# --- 18: read with doublequote=False -----------------------------------
_r = random.Random(4048)
_cases = []
for _i in range(300):
    _d = _ora_dialect(_r, quotings=["minimal", "all"], dqs=[False], sis=[False])
    _cases.append((_ora_text(_r, _d), _d))
check("read: doublequote=False", _ora_rprobe(_cases))

# --- 19: read with skipinitialspace=True -------------------------------
_r = random.Random(4049)
_cases = []
for _i in range(300):
    _d = _ora_dialect(_r, quotings=["minimal", "all"], sis=[True])
    _cases.append((_ora_text(_r, _d), _d))
check("read: skipinitialspace=True", _ora_rprobe(_cases))

# --- 20-21: read with quoting='nonnumeric' -----------------------------
_r = random.Random(4050)
_cases = []
_good = 0
while len(_cases) < 400:
    _d = _ora_dialect(_r, quotings=["nonnumeric"])
    if _r.random() < 0.5:
        _t2 = _ora_text(_r, _d)
    else:
        _t2 = "".join(_r.choice(["0", "1", "2", ".", "-", "e", " ",
                                 _d["delimiter"], _d["quotechar"], "\n"])
                      for _ in range(_r.randint(0, 10)))
    _ok = _ora_read(_t2, _d) != ("ERR",)
    if _ok:
        _good += 1
    if _ok or _good * 3 > len(_cases):
        _cases.append((_t2, _d))
for _k, _part in enumerate(_ora_split(_cases, 2)):
    check("read: nonnumeric conversion, part %d" % (_k + 1), _ora_rprobe(_part))

# --- 22: read with quoting='none' --------------------------------------
_r = random.Random(4051)
_cases = []
for _i in range(300):
    _d = _ora_dialect(_r, quotings=["none"])
    _cases.append((_ora_text(_r, _d), _d))
check("read: quoting='none'", _ora_rprobe(_cases))

# --- 23-24: hand-picked reader corner cases ----------------------------
_BS = _ora_BS
_D = dict(delimiter=",", quotechar='"', escapechar=None, doublequote=True,
          quoting="minimal", lineterminator="\r\n", skipinitialspace=False)


def _ora_d(**kw):
    d = dict(_D)
    d.update(kw)
    return d


_corner = [
    ('"ab"cd,e\r\n', _ora_d()),
    ('"ab" cd\r\n', _ora_d()),
    ('a"b,c\r\n', _ora_d()),
    ('a""b\r\n', _ora_d()),
    (' "ab",c\r\n', _ora_d()),
    (' "ab" , c\r\n', _ora_d(skipinitialspace=True)),
    ('a, b ,  "c d" ,e\r\n', _ora_d(skipinitialspace=True)),
    ('a,   ,b\r\n', _ora_d(skipinitialspace=True)),
    ("", _ora_d()),
    ("\r\n", _ora_d()),
    ("a\r\n\r\n", _ora_d()),
    ("a\r\rb", _ora_d()),
    ("a\nb\n", _ora_d(lineterminator="\r\n")),
    ("a,b", _ora_d()),
    ("a,", _ora_d()),
    (",", _ora_d()),
    ('"abc\r\n', _ora_d()),
    ('a,"bc', _ora_d()),
    ('"', _ora_d()),
    ('"a\rb"\r\n', _ora_d()),
    ('"a""b"\r\n', _ora_d(doublequote=False, escapechar=_BS)),
    ('"a' + _BS + '"b",c\r\n', _ora_d(escapechar=_BS)),
    ('a' + _BS + ',b,c\r\n', _ora_d(escapechar=_BS)),
    (_BS + '"a",b\r\n', _ora_d(escapechar=_BS)),
    ('ab' + _BS, _ora_d(escapechar=_BS)),
    ('a' + _BS + '\r\nb\r\n', _ora_d(escapechar=_BS)),
    ('a' + _BS + '\rb\r\n', _ora_d(escapechar=_BS)),
    ('"a,b",c\r\n', _ora_d(quoting="none")),
    ('a' + _BS + ',b\r\n', _ora_d(quoting="none", escapechar=_BS)),
    ('"a"b,1\r\n', _ora_d(quoting="nonnumeric")),
    (',\r\n', _ora_d(quoting="nonnumeric")),
    ('  \r\n', _ora_d(quoting="nonnumeric")),
    ('  \r\n', _ora_d(quoting="nonnumeric", skipinitialspace=True)),
    (_BS + '12,3\r\n', _ora_d(quoting="nonnumeric", escapechar=_BS)),
    ('x\r\n', _ora_d(quoting="nonnumeric")),
    ('1,"2"\r\n', _ora_d(quoting="all")),
]
for _k, _part in enumerate(_ora_split(_corner, 2)):
    check("read: corner cases, part %d" % (_k + 1), _ora_rprobe(_part))

# --- 25: round trip through the candidate ------------------------------
_r = random.Random(4052)


def _ora_roundtrip():
    for _i in range(400):
        d = _ora_dialect(_r)
        fields = _ora_fields(_r, d, numeric=True)
        want = _ora_write(fields, d)
        got = _ora_cand_write(fields, d)
        if want != got:
            return False
        if isinstance(want, tuple):
            continue
        if _ora_read(want, d) != _ora_cand_read(got, d):
            return False
    return True


check("round trip: write_row then read_rows", _ora_roundtrip)

_t.cancel()
report()
