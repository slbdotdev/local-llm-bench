import json
import os
import subprocess
import sys
import tempfile

TOTAL = 36
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
    import trender  # noqa: F401
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


# ---------------------------------------------------------------- case table
# (group, key, template, ctx, expected)
# expected is ("out", text) or ("err", kind); an optional third element True
# additionally demands that render left the caller's ctx dict untouched.
O = "out"
E = "err"

IFEL = "{% if a %}A{% elif b %}B{% else %}C{% endif %}"
BOX = "[{% if x %}Y{% endif %}]"

CASES = [
    ("literal text", "l1", "", {}, (O, "")),
    ("literal text", "l2", "hello, world", {}, (O, "hello, world")),
    ("literal text", "l3", "a } b %} c }} d { e % f", {}, (O, "a } b %} c }} d { e % f")),
    ("literal text", "l4", "one\ntwo\n", {}, (O, "one\ntwo\n")),

    ("interpolation of values and literals", "i1", "{{ s }}", {"s": "hi"}, (O, "hi")),
    ("interpolation of values and literals", "i2", "[{{ n }}]", {"n": 7}, (O, "[7]")),
    ("interpolation of values and literals", "i3", "{{ n }}{{ s }}", {"n": 0, "s": "x"}, (O, "0x")),
    ("interpolation of values and literals", "i4", "{{ 42 }}", {}, (O, "42")),
    ("interpolation of values and literals", "i5", "{{ 'a b' }}", {}, (O, "a b")),
    ("interpolation of values and literals", "i6", "{{ 'a|b' }}", {}, (O, "a|b")),
    ("interpolation of values and literals", "i7", "{{ 'a}}b' }}", {}, (O, "a}}b")),
    ("interpolation of values and literals", "i8", "[{{ '' }}]", {}, (O, "[]")),

    ("dotted path lookup", "p1", "{{ user.name }}", {"user": {"name": "ada"}}, (O, "ada")),
    ("dotted path lookup", "p2", "{{ a.b.c }}", {"a": {"b": {"c": "deep"}}}, (O, "deep")),
    ("dotted path lookup", "p3", "{{ a.b }}", {"a": {"b": 3}}, (O, "3")),

    ("list and tuple indexing", "x1", "{{ xs.1 }}", {"xs": ["p", "q"]}, (O, "q")),
    ("list and tuple indexing", "x2", "{{ items.0.name }}",
     {"items": [{"name": "ann"}, {"name": "bob"}]}, (O, "ann")),
    ("list and tuple indexing", "x3", "{{ t.1 }}", {"t": ("p", "q")}, (O, "q")),
    ("list and tuple indexing", "x4", "{{ m.0.1 }}", {"m": [["a", "b"]]}, (O, "b")),

    ("missing paths render empty", "m1", "[{{ nope }}]", {}, (O, "[]")),
    ("missing paths render empty", "m2", "[{{ a.b }}]", {"a": {"z": 1}}, (O, "[]")),
    ("missing paths render empty", "m3", "[{{ xs.9 }}]", {"xs": [1]}, (O, "[]")),
    ("missing paths render empty", "m4", "[{{ n.x }}]", {"n": 7}, (O, "[]")),
    ("missing paths render empty", "m5", "[{{ xs.x }}]", {"xs": [1]}, (O, "[]")),

    ("upper and lower filters", "f1", "{{ s|upper }}/{{ s | lower }}", {"s": "aB"}, (O, "AB/ab")),
    ("upper and lower filters", "f2", "[{{ nope|upper }}]", {}, (O, "[]")),

    ("len filter", "f3", "{{ s|len }}", {"s": "abcd"}, (O, "4")),
    ("len filter", "f4", "{{ xs|len }}", {"xs": [1, 2, 3]}, (O, "3")),
    ("len filter", "f5", "{{ d|len }}", {"d": {"a": 1, "b": 2}}, (O, "2")),
    ("len filter", "f6", "{{ t|len }}", {"t": (1,)}, (O, "1")),
    ("len filter", "f7", "{{ nope|len }}", {}, (O, "0")),

    ("filter chaining", "f8", "{{ s|upper|len }}", {"s": "abc"}, (O, "3")),
    ("filter chaining", "f9", "{{ u.n|upper|lower }}", {"u": {"n": "AdA"}}, (O, "ada")),

    ("escaping of & < > and quote", "e1", "{{ s }}", {"s": '<a href="x">&'},
     (O, "&lt;a href=&quot;x&quot;&gt;&amp;")),
    ("escaping of & < > and quote", "e2", "{{ s }}", {"s": "no specials"}, (O, "no specials")),
    ("escaping of & < > and quote", "e3", "{{ 'a<b' }}", {}, (O, "a&lt;b")),

    ("escaping replaces & first", "e4", "{{ s }}", {"s": "a&lt;b"}, (O, "a&amp;lt;b")),
    ("escaping replaces & first", "e5", "{{ s }}", {"s": "&amp;"}, (O, "&amp;amp;")),
    ("escaping replaces & first", "e6", "{{ s }}", {"s": "&<"}, (O, "&amp;&lt;")),

    ("raw filter", "r1", "{{ s|raw }}", {"s": '<b>&"'}, (O, '<b>&"')),
    ("raw filter", "r2", "{{ s|raw }}|{{ s }}", {"s": "<b>"}, (O, "<b>|&lt;b&gt;")),

    ("raw and esc in non-final positions", "r3", "{{ s|raw|upper }}", {"s": "<b>"}, (O, "<B>")),
    ("raw and esc in non-final positions", "r4", "{{ s|raw|len }}", {"s": "<b>"}, (O, "3")),
    ("raw and esc in non-final positions", "r5", "{{ s|esc|upper }}", {"s": "<b>"}, (O, "&lt;B&gt;")),
    ("raw and esc in non-final positions", "r6", "{{ s|raw|upper|len }}", {"s": "<b>"}, (O, "3")),

    ("last raw or esc wins", "r7", "{{ s|raw|esc }}", {"s": "<b>"}, (O, "&lt;b&gt;")),
    ("last raw or esc wins", "r8", "{{ s|esc|raw }}", {"s": "<b>"}, (O, "<b>")),
    ("last raw or esc wins", "r9", "{{ s|raw|upper|esc }}", {"s": "<b>"}, (O, "&lt;B&gt;")),
    ("last raw or esc wins", "r10", "{{ s|esc|upper|raw }}", {"s": "<b>"}, (O, "<B>")),

    ("whitespace control on block tags", "w1",
     "a\n   {%- if 1 -%}\n   b\n   {%- endif -%}\n   c", {}, (O, "abc")),
    ("whitespace control on block tags", "w2", "a  {%- if 1 %}X{% endif %}", {}, (O, "aX")),
    ("whitespace control on block tags", "w3", "{% if 1 -%}   \n  X{% endif %}", {}, (O, "X")),
    ("whitespace control on block tags", "w4", "a {% if 1 %} X {% endif %} b", {},
     (O, "a  X  b")),

    ("whitespace control on interpolation tags", "w5", "x   {{- s -}}\n\n   y", {"s": "S"},
     (O, "xSy")),
    ("whitespace control on interpolation tags", "w6", "x {{ s -}}  y", {"s": "S"}, (O, "x Sy")),
    ("whitespace control on interpolation tags", "w7", "x  {{- s }} y", {"s": "S"}, (O, "xS y")),

    ("whitespace control edge cases", "w8", "   {{- 'a' }}", {}, (O, "a")),
    ("whitespace control edge cases", "w9", "{{ 'a' -}}   \n ", {}, (O, "a")),
    ("whitespace control edge cases", "w10", "A {{- 'x' -}} B", {}, (O, "AxB")),
    ("whitespace control edge cases", "w11", "{{ 'a' -}}{{- 'b' }}", {}, (O, "ab")),
    ("whitespace control edge cases", "w12", "a\t\r\n {{- 'x' }}", {}, (O, "ax")),

    ("if elif else selection", "c1", IFEL, {"a": 1}, (O, "A")),
    ("if elif else selection", "c2", IFEL, {"a": 0, "b": 1}, (O, "B")),
    ("if elif else selection", "c3", IFEL, {"a": 0, "b": 0}, (O, "C")),
    ("if elif else selection", "c4",
     "{% if a %}A{% elif b %}B{% elif c %}C{% else %}D{% endif %}",
     {"a": 0, "b": 0, "c": 1}, (O, "C")),

    ("truthiness and missing else", "c5", BOX, {"x": 0}, (O, "[]")),
    ("truthiness and missing else", "c6", BOX, {"x": ""}, (O, "[]")),
    ("truthiness and missing else", "c7", BOX, {"x": []}, (O, "[]")),
    ("truthiness and missing else", "c8", BOX, {"x": {}}, (O, "[]")),
    ("truthiness and missing else", "c9", BOX, {}, (O, "[]")),
    ("truthiness and missing else", "c10", BOX, {"x": "0"}, (O, "[Y]")),
    ("truthiness and missing else", "c11", BOX, {"x": [0]}, (O, "[Y]")),

    ("conditions may use filters", "c12", "{% if xs|len %}Y{% else %}N{% endif %}",
     {"xs": []}, (O, "N")),
    ("conditions may use filters", "c13", "{% if xs|len %}Y{% else %}N{% endif %}",
     {"xs": [1]}, (O, "Y")),
    ("conditions may use filters", "c14", "{% if s|upper %}Y{% else %}N{% endif %}",
     {"s": ""}, (O, "N")),

    ("nested ifs", "c15", "{% if a %}{% if b %}AB{% else %}A{% endif %}{% else %}N{% endif %}",
     {"a": 1, "b": 1}, (O, "AB")),
    ("nested ifs", "c16", "{% if a %}{% if b %}AB{% else %}A{% endif %}{% else %}N{% endif %}",
     {"a": 1, "b": 0}, (O, "A")),
    ("nested ifs", "c17", "{% if a %}{% if b %}AB{% else %}A{% endif %}{% else %}N{% endif %}",
     {"a": 0, "b": 1}, (O, "N")),

    ("for basics with loop.index", "g1",
     "{% for w in ws %}{{ loop.index }}{{ loop.index0 }}{{ w }};{% endfor %}",
     {"ws": ["a", "b"]}, (O, "10a;21b;")),
    ("for basics with loop.index", "g2", "{% for w in t %}{{ w }}{% endfor %}",
     {"t": ("p", "q")}, (O, "pq")),
    ("for basics with loop.index", "g3", "{% for w in ws %}{{ w }}{% endfor %}",
     {"ws": [1, 2]}, (O, "12")),

    ("loop.first and loop.last", "g4",
     "{% for w in ws %}{{ loop.first }}{{ loop.last }},{% endfor %}", {"ws": [1, 2, 3]},
     (O, "TrueFalse,FalseFalse,FalseTrue,")),
    ("loop.first and loop.last", "g5",
     "{% for w in ws %}{% if loop.first %}[{% endif %}{{ w }}"
     "{% if loop.last %}]{% endif %}{% endfor %}", {"ws": ["a", "b"]}, (O, "[ab]")),

    ("for with empty branch", "g6", "{% for w in ws %}x{% empty %}none{% endfor %}",
     {"ws": []}, (O, "none")),
    ("for with empty branch", "g7", "[{% for w in ws %}x{% endfor %}]", {"ws": []}, (O, "[]")),
    ("for with empty branch", "g8", "{% for w in ws %}{{ w }}{% empty %}none{% endfor %}",
     {"ws": ["a"]}, (O, "a")),
    ("for with empty branch", "g9", "{% for w in ws %}x{% empty %}{{ w }}{% endfor %}",
     {"ws": [], "w": "outer"}, (O, "outer")),

    ("nested for keeps the outer loop", "g10",
     "{% for a in xs %}{% for b in ys %}{{ b }}{{ loop.index }}{% endfor %}"
     "-{{ loop.index }}{{ a }};{% endfor %}", {"xs": ["A", "B"], "ys": ["y"]},
     (O, "y1-1A;y1-2B;")),
    ("nested for keeps the outer loop", "g11",
     "{% for a in xs %}{% for a in ys %}{{ a }}{% endfor %}{{ a }}{% endfor %}",
     {"xs": ["A", "B"], "ys": ["z"]}, (O, "zAzB")),

    ("loop variable shadows and is restored", "g12",
     "{% for w in ws %}{{ w }}{% endfor %}[{{ w }}]", {"ws": ["a", "b"], "w": "outer"},
     (O, "ab[outer]")),
    ("loop variable shadows and is restored", "g13",
     "{% for w in ws %}x{% endfor %}[{{ w }}]", {"ws": [], "w": "outer"}, (O, "[outer]")),
    ("loop variable shadows and is restored", "g14",
     "{% for w in ws %}x{% endfor %}[{{ w }}]", {"ws": ["a"]}, (O, "x[]")),
    ("loop variable shadows and is restored", "g15",
     "[{{ loop.index }}]{% for w in ws %}{% endfor %}[{{ loop }}]",
     {"ws": ["a"], "loop": "L"}, (O, "[][L]")),

    ("context dict is left unchanged", "u1", "{% for w in ws %}{{ w }}{% endfor %}",
     {"ws": ["a"], "w": "outer"}, (O, "a", True)),
    ("context dict is left unchanged", "u2",
     "{% for w in ws %}{% for w in ws %}{% endfor %}{% endfor %}", {"ws": ["a", "b"]},
     (O, "", True)),
    ("context dict is left unchanged", "u3", "{% for w in ws %}x{% empty %}y{% endfor %}",
     {"ws": [], "loop": "L", "w": 1}, (O, "y", True)),
    ("context dict is left unchanged", "u4", "{% for w in ws %}{{ w|nope }}{% endfor %}",
     {"ws": ["a"], "w": "outer"}, (E, "filter", True)),

    ("syntax errors in tags and expressions", "s1", "{{ }}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s2", "{{    }}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s3", "{{ a b }}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s4", "{{ 1x }}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s5", "{{ a. }}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s6", "{{ x | }}", {"x": "a"}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s7", "{{ x|| }}", {"x": "a"}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s8", "{% foo %}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s9", "{% bar 1 %}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s10", "{% %}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s11", "{% if %}{% endif %}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s12", "{% for w %}{% endfor %}", {}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s13", "{% for w in %}{% endfor %}", {},
     (E, "syntax")),
    ("syntax errors in tags and expressions", "s14", "{% for 1 in ws %}{% endfor %}",
     {"ws": []}, (E, "syntax")),
    ("syntax errors in tags and expressions", "s15", "{% if 1 %}{% endif x %}", {},
     (E, "syntax")),
    ("syntax errors in tags and expressions", "s16", "{% if 1 %}{% else x %}{% endif %}", {},
     (E, "syntax")),
    ("syntax errors in tags and expressions", "s17",
     "{% for w in ws %}{% empty x %}{% endfor %}", {"ws": []}, (E, "syntax")),

    ("syntax errors for unclosed tags and strings", "s18", "{{ x", {"x": "a"}, (E, "syntax")),
    ("syntax errors for unclosed tags and strings", "s19", "{% if 1", {}, (E, "syntax")),
    ("syntax errors for unclosed tags and strings", "s20", "a {{ b }} tail {% c", {},
     (E, "syntax")),
    ("syntax errors for unclosed tags and strings", "s21", "{{ 'abc }}", {}, (E, "syntax")),
    ("syntax errors for unclosed tags and strings", "s22", "{% if 'abc %}{% endif %}", {},
     (E, "syntax")),
    ("syntax errors for unclosed tags and strings", "s23", "text {{-", {}, (E, "syntax")),

    ("unclosed block errors", "n1", "{% if 1 %}x", {}, (E, "unclosed")),
    ("unclosed block errors", "n2", "{% for w in ws %}", {"ws": []}, (E, "unclosed")),
    ("unclosed block errors", "n3", "{% if 1 %}{% else %}", {}, (E, "unclosed")),
    ("unclosed block errors", "n4", "{% for w in ws %}{% empty %}", {"ws": []}, (E, "unclosed")),
    ("unclosed block errors", "n5", "{% if 1 %}{% if 1 %}{% endif %}", {}, (E, "unclosed")),

    ("mismatched closing tags", "b1", "{% if 1 %}{% endfor %}", {}, (E, "mismatch")),
    ("mismatched closing tags", "b2", "{% for w in ws %}{% endif %}", {"ws": []},
     (E, "mismatch")),
    ("mismatched closing tags", "b3", "{% endif %}", {}, (E, "mismatch")),
    ("mismatched closing tags", "b4", "{% endfor %}", {}, (E, "mismatch")),
    ("mismatched closing tags", "b5", "x{% if 1 %}{% endif %}{% endif %}", {}, (E, "mismatch")),

    ("mismatched branch tags", "b6", "{% if 1 %}{% else %}{% else %}{% endif %}", {},
     (E, "mismatch")),
    ("mismatched branch tags", "b7", "{% if 1 %}{% else %}{% elif 1 %}{% endif %}", {},
     (E, "mismatch")),
    ("mismatched branch tags", "b8", "{% if 1 %}{% empty %}{% endif %}", {}, (E, "mismatch")),
    ("mismatched branch tags", "b9", "{% for w in ws %}{% else %}{% endfor %}", {"ws": []},
     (E, "mismatch")),
    ("mismatched branch tags", "b10", "{% else %}", {}, (E, "mismatch")),
    ("mismatched branch tags", "b11", "{% elif 1 %}", {}, (E, "mismatch")),
    ("mismatched branch tags", "b12", "{% empty %}", {}, (E, "mismatch")),
    ("mismatched branch tags", "b13", "{% for w in ws %}{% empty %}{% empty %}{% endfor %}",
     {"ws": []}, (E, "mismatch")),

    ("unknown filter errors", "k1", "{{ s|nope }}", {"s": "a"}, (E, "filter")),
    ("unknown filter errors", "k2", "{{ s|Upper }}", {"s": "a"}, (E, "filter")),
    ("unknown filter errors", "k3", "{{ s|upper|nope }}", {"s": "a"}, (E, "filter")),
    ("unknown filter errors", "k4", "{% if s|nope %}{% endif %}", {"s": "a"}, (E, "filter")),
    ("unknown filter errors", "k5", "{% for w in ws|nope %}{% endfor %}", {"ws": []},
     (E, "filter")),

    ("type errors from filters and rendering", "t1", "{{ 5|len }}", {}, (E, "type")),
    ("type errors from filters and rendering", "t2", "{{ 5|upper }}", {}, (E, "type")),
    ("type errors from filters and rendering", "t3", "{{ xs|lower }}", {"xs": [1]}, (E, "type")),
    ("type errors from filters and rendering", "t4", "{{ xs }}", {"xs": [1]}, (E, "type")),
    ("type errors from filters and rendering", "t5", "{{ d }}", {"d": {"a": 1}}, (E, "type")),
    ("type errors from filters and rendering", "t6", "{{ xs|len|upper }}", {"xs": [1]},
     (E, "type")),

    ("type errors from for iterables", "t7", "{% for w in n %}{% endfor %}", {"n": 5},
     (E, "type")),
    ("type errors from for iterables", "t8", "{% for w in s %}{% endfor %}", {"s": "abc"},
     (E, "type")),
    ("type errors from for iterables", "t9", "{% for w in d %}{% endfor %}", {"d": {"a": 1}},
     (E, "type")),
    ("type errors from for iterables", "t10", "{% for w in nope %}x{% empty %}y{% endfor %}",
     {}, (E, "type")),
    ("type errors from for iterables", "t11", "{% for w in 'ab' %}{% endfor %}", {},
     (E, "type")),

    ("error precedence: earlier pass wins", "z1", "{% if 1 %}{{ y", {}, (E, "syntax")),
    ("error precedence: earlier pass wins", "z2", "{% if 1 %}{{ x|nope }}", {"x": "a"},
     (E, "unclosed")),
    ("error precedence: earlier pass wins", "z3", "{% if 1 %}{% endfor %}{{ }}", {},
     (E, "mismatch")),
    ("error precedence: earlier pass wins", "z4", "{% badtag %}{% endif %}", {}, (E, "syntax")),
    ("error precedence: earlier pass wins", "z5", "{% for w in nope %}{% endfor %}{% endif %}",
     {}, (E, "mismatch")),

    ("error precedence: unrendered branches", "z6", "{% if 0 %}{{ }}{% endif %}", {},
     (E, "syntax")),
    ("error precedence: unrendered branches", "z7", "{% if 0 %}{{ x|nope }}{% endif %}",
     {"x": "a"}, (O, "")),
    ("error precedence: unrendered branches", "z8", "{% if 0 %}{% badtag %}{% endif %}", {},
     (E, "syntax")),
    ("error precedence: unrendered branches", "z9", "{{ 5|len|nope }}", {}, (E, "type")),
    ("error precedence: unrendered branches", "z10", "{{ x|nope|len }}", {"x": "ab"},
     (E, "filter")),
]

GROUPS = []
for _c in CASES:
    if _c[0] not in GROUPS:
        GROUPS.append(_c[0])

assert len(GROUPS) == TOTAL, len(GROUPS)

CHILD = r'''
import ast, copy, json, os, sys
sys.path.insert(0, os.getcwd())
import trender
TE = getattr(trender, "TemplateError", None)
if not (isinstance(TE, type) and issubclass(TE, BaseException)):
    TE = None
cases = json.load(open(sys.argv[1]))
for key, tmpl, ctx_src in cases:
    ctx = ast.literal_eval(ctx_src)
    before = copy.deepcopy(ctx)
    try:
        out = trender.render(tmpl, ctx)
        res = ["ok", out, ctx == before]
        if not isinstance(out, str):
            res = ["exc", "not-a-string"]
    except Exception as e:
        kind = getattr(e, "kind", None)
        if TE is not None and isinstance(e, TE) and isinstance(e, ValueError) \
                and isinstance(kind, str):
            res = ["err", kind, ctx == before]
        else:
            res = ["exc", type(e).__name__]
    sys.stdout.write(json.dumps([key, res]) + "\n")
    sys.stdout.flush()
'''

_tmp = tempfile.mkdtemp(prefix="tmplgrade_")
_script = os.path.join(_tmp, "_child.py")
with open(_script, "w") as fh:
    fh.write(CHILD)
_casefile = os.path.join(_tmp, "_cases.json")


def run_all(cases):
    """Run every case in a subprocess; a hang costs only its own case."""
    got = {}
    pending = [(k, t, repr(c)) for _g, k, t, c, _e in cases]
    rounds = 0
    while pending and rounds < 3:
        rounds += 1
        with open(_casefile, "w") as fh:
            json.dump(pending, fh)
        out = ""
        try:
            r = subprocess.run([sys.executable, _script, _casefile],
                               capture_output=True, text=True, timeout=12)
            out = r.stdout or ""
        except subprocess.TimeoutExpired as exc:
            o = exc.output
            out = o if isinstance(o, str) else (o or b"").decode("utf-8", "replace")
        except Exception:
            out = ""
        for line in out.splitlines():
            try:
                k, v = json.loads(line)
            except Exception:
                continue
            got[k] = v
        pending = [c for c in pending if c[0] not in got]
        if pending:
            got[pending[0][0]] = ["exc", "timeout-or-crash"]
            pending = pending[1:]
    for _g, k, _t, _c, _e in cases:
        got.setdefault(k, ["exc", "no-result"])
    return got


RESULTS = run_all(CASES)


def matches(exp, res):
    if not isinstance(res, list) or not res:
        return False
    if exp[0] == O:
        if res[0] != "ok" or len(res) < 3 or res[1] != exp[1]:
            return False
    else:
        if res[0] != "err" or len(res) < 3 or res[1] != exp[1]:
            return False
    if len(exp) > 2 and exp[2] and res[2] is not True:
        return False
    return True


def group_probe(gname):
    def probe():
        for g, k, _t, _c, exp in CASES:
            if g == gname and not matches(exp, RESULTS.get(k)):
                return False
        return True
    return probe


for _g in GROUPS:
    check(_g, group_probe(_g))

report()
