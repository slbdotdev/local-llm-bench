"""Validate every hidden grader against a known-good reference solution."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "tasks")

REFS = {}

REFS["01_rle"] = {"rle.py": '''
def encode(s):
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(f"{j-i}{s[i]}"); i = j
    return "".join(out)

def decode(s):
    out = []; num = ""
    for ch in s:
        if ch.isdigit(): num += ch
        else: out.append(ch * int(num)); num = ""
    return "".join(out)
'''}

REFS["02_lru"] = {"lru.py": '''
from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity):
        if capacity < 1: raise ValueError
        self.cap = capacity; self.d = OrderedDict()
    def get(self, key):
        if key not in self.d: return -1
        self.d.move_to_end(key); return self.d[key]
    def put(self, key, value):
        if key in self.d: self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.cap: self.d.popitem(last=False)
    def __len__(self): return len(self.d)
    def keys(self): return list(self.d.keys())
'''}

REFS["03_calc"] = {"calc.py": '''
import re
TOK = re.compile(r"(?:(\\d+\\.\\d*|\\.\\d+|\\d+)|(.))")
def tokenize(s):
    toks = []; pos = 0
    while pos < len(s):
        if s[pos].isspace(): pos += 1; continue
        m = TOK.match(s, pos)
        if not m or m.end() == pos: break
        pos = m.end()
        if m.group(1): toks.append(("num", float(m.group(1))))
        elif m.group(2):
            if m.group(2) not in "+-*/()": raise ValueError("bad char")
            toks.append(("op", m.group(2)))
    if pos < len(s) and s[pos:].strip(): raise ValueError
    return toks
class P:
    def __init__(self, toks): self.t = toks; self.i = 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else (None, None)
    def take(self): v = self.peek(); self.i += 1; return v
    def expr(self):
        v = self.term()
        while self.peek() == ("op", "+") or self.peek() == ("op", "-"):
            op = self.take()[1]; r = self.term(); v = v + r if op == "+" else v - r
        return v
    def term(self):
        v = self.unary()
        while self.peek() == ("op", "*") or self.peek() == ("op", "/"):
            op = self.take()[1]; r = self.unary()
            if op == "*": v *= r
            else:
                if r == 0: raise ZeroDivisionError
                v /= r
        return v
    def unary(self):
        if self.peek() == ("op", "-"): self.take(); return -self.unary()
        return self.atom()
    def atom(self):
        k, v = self.take()
        if k == "num": return v
        if (k, v) == ("op", "("):
            r = self.expr()
            if self.take() != ("op", ")"): raise ValueError
            return r
        raise ValueError
def evaluate(expr):
    toks = tokenize(expr)
    if not toks: raise ValueError
    p = P(toks); v = p.expr()
    if p.i != len(toks): raise ValueError
    return float(v)
'''}

REFS["04_csv"] = {"csvlite.py": '''
def parse(text):
    rows = []; row = []; field = []; i = 0; n = len(text); inq = False; started = False
    while i < n:
        c = text[i]
        if inq:
            if c == '"':
                if i + 1 < n and text[i+1] == '"': field.append('"'); i += 2; continue
                inq = False; i += 1; continue
            field.append(c); i += 1; continue
        if c == '"': inq = True; started = True; i += 1; continue
        if c == ",": row.append("".join(field)); field = []; started = True; i += 1; continue
        if c == "\\r" and i + 1 < n and text[i+1] == "\\n": i += 1; c = "\\n"
        if c == "\\n":
            row.append("".join(field)); rows.append(row); row = []; field = []; started = False; i += 1; continue
        field.append(c); started = True; i += 1
    if started or field or row:
        row.append("".join(field)); rows.append(row)
    return rows
'''}

REFS["05_bugfix"] = {"inventory.py": '''
class Item:
    def __init__(self, sku, name, qty, unit_price, tags=None):
        self.sku = sku; self.name = name; self.qty = qty; self.unit_price = unit_price
        self.tags = list(tags) if tags else []
    def add_tag(self, tag): self.tags.append(tag)
    def value(self): return self.qty * self.unit_price
def restock(items, sku, amount):
    if amount <= 0: raise ValueError("amount must be positive")
    for it in items:
        if it.sku == sku: it.qty += amount; return it.qty
    raise KeyError(sku)
def low_stock(items, threshold):
    return sorted(it.sku for it in items if it.qty < threshold)
def total_value(items):
    return round(sum(it.value() for it in items), 2)
def apply_discount(items, tag, percent):
    n = 0
    for it in items:
        if tag in it.tags: it.unit_price = round(it.unit_price * (1 - percent / 100), 2); n += 1
    return n
def find(items, query):
    q = query.lower()
    return [it for it in items if q in it.name.lower()]
'''}

REFS["06_refactor"] = {
    "shop/pricing.py": '''
def line_total(item):
    return round(item["price"] * item["qty"], 2)
def compute_total(items, *, tax_rate=0.0):
    subtotal = sum(line_total(i) for i in items)
    return round(subtotal * (1 + tax_rate), 2)
''',
    "shop/cart.py": '''
from .pricing import compute_total, line_total
class Cart:
    def __init__(self, tax=0.0): self.items = []; self.tax = tax
    def add(self, name, price, qty=1): self.items.append({"name": name, "price": price, "qty": qty})
    def subtotal(self): return round(sum(line_total(i) for i in self.items), 2)
    def checkout(self): return compute_total(self.items, tax_rate=self.tax)
''',
    "shop/report.py": '''
from shop import pricing
def daily_report(orders, tax):
    totals = [pricing.compute_total(o, tax_rate=tax) for o in orders]
    return len(totals), round(sum(totals), 2)
def untaxed_report(orders):
    return [pricing.compute_total(o) for o in orders]
''',
    "shop/cli.py": '''
from shop.cart import Cart
from shop.report import daily_report
from shop.pricing import compute_total as ct
def main():
    c = Cart(tax=0.1); c.add("pen", 1.5, 4); c.add("book", 12.0)
    print("cart:", c.checkout())
    orders = [[{"name": "a", "price": 2.0, "qty": 3}], [{"name": "b", "price": 5.5, "qty": 2}]]
    print("report:", daily_report(orders, 0.05))
    print("raw:", ct(orders[0], tax_rate=0.0))
if __name__ == "__main__": main()
'''}

REFS["07_dijkstra"] = {"graph.py": '''
import heapq
def shortest_path(graph, src, dst):
    nodes = set(graph) | {n for d in graph.values() for n in d}
    if src not in nodes: raise KeyError(src)
    if src == dst: return (0, [src])
    dist = {src: 0}; prev = {}; pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")): continue
        if u == dst: break
        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if dst not in dist: return (None, [])
    path = [dst]
    while path[-1] != src: path.append(prev[path[-1]])
    return (dist[dst], path[::-1])
'''}

REFS["08_topo"] = {"deps.py": '''
import heapq
class CycleError(ValueError):
    def __init__(self, cycle):
        super().__init__(f"cycle: {cycle}"); self.cycle = cycle
def resolve(deps):
    nodes = set(deps) | {d for v in deps.values() for d in v}
    indeg = {n: 0 for n in nodes}; children = {n: [] for n in nodes}
    for x, ds in deps.items():
        for d in ds: indeg[x] += 1; children[d].append(x)
    heap = [n for n in nodes if indeg[n] == 0]; heapq.heapify(heap); out = []
    while heap:
        n = heapq.heappop(heap); out.append(n)
        for c in children[n]:
            indeg[c] -= 1
            if indeg[c] == 0: heapq.heappush(heap, c)
    if len(out) != len(nodes):
        rem = {n for n in nodes if n not in out}
        start = min(rem); path = [start]; seen = {start}; cur = start
        while True:
            nxt = next(d for d in deps.get(cur, []) if d in rem)
            if nxt in seen:
                cyc = path[path.index(nxt):] + [nxt]; raise CycleError(cyc)
            path.append(nxt); seen.add(nxt); cur = nxt
    return out
'''}

REFS["09_wc"] = {"wc.py": '''
import sys
from collections import Counter
def main(argv):
    top = None; args = list(argv)
    if args and args[0] == "--top": top = int(args[1]); args = args[2:]
    path = args[0]
    try:
        with open(path, encoding="utf-8", newline="") as f: text = f.read()
    except FileNotFoundError:
        print("error: no such file", file=sys.stderr); sys.exit(2)
    if top is None:
        print(text.count("\\n"), len(text.split()), len(text)); return
    words = [w.lower().strip(".,;:!?\\"'()[]") for w in text.split()]
    c = Counter(w for w in words if w)
    for w, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:top]: print(w, n)
if __name__ == "__main__": main(sys.argv[1:])
'''}

REFS["10_intervals"] = {"intervals.py": '''
def _chk(iv):
    for a, b in iv:
        if a > b: raise ValueError((a, b))
def merge(intervals):
    _chk(intervals); out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1] + 1: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out
def insert(intervals, new):
    _chk(intervals); _chk([new]); return merge(list(intervals) + [new])
def total_length(intervals):
    return sum(b - a + 1 for a, b in merge(intervals))
'''}

REFS["11_roman"] = {"roman.py": '''
VALS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
def to_roman(n):
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 3999: raise ValueError(n)
    out = ""
    for v, s in VALS:
        while n >= v: out += s; n -= v
    return out
def from_roman(s):
    if not isinstance(s, str) or not s: raise ValueError(s)
    m = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    if any(c not in m for c in s): raise ValueError(s)
    total = 0
    for i, c in enumerate(s):
        v = m[c]
        if i + 1 < len(s) and m[s[i+1]] > v: total -= v
        else: total += v
    if not 1 <= total <= 3999 or to_roman(total) != s: raise ValueError(s)
    return total
'''}


def main():
    bad = 0
    for name in sorted(os.listdir(T)):
        d = os.path.join(T, name)
        if not os.path.isdir(d): continue
        sb = tempfile.mkdtemp(prefix="selftest_")
        seed = os.path.join(d, "seed")
        if os.path.isdir(seed): shutil.copytree(seed, sb, dirs_exist_ok=True)
        for fn, content in REFS.get(name, {}).items():
            p = os.path.join(sb, fn); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f: f.write(content.lstrip())
        # Untouched seed must FAIL the grader (for seeded tasks), reference must PASS.
        shutil.copy(os.path.join(d, "test.py"), os.path.join(sb, "_hidden_test.py"))
        r = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, capture_output=True, text=True, encoding="utf-8", timeout=120)
        ok = r.returncode == 0 and "PASS" in r.stdout
        print(f"{name:14s} ref  {'PASS' if ok else 'FAIL'}  {(r.stdout + r.stderr).strip()[-300:] if not ok else ''}")
        bad += not ok
        if os.path.isdir(seed):
            sb2 = tempfile.mkdtemp(prefix="selftest_"); shutil.copytree(seed, sb2, dirs_exist_ok=True)
            shutil.copy(os.path.join(d, "test.py"), os.path.join(sb2, "_hidden_test.py"))
            r = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb2, capture_output=True, text=True, encoding="utf-8", timeout=120)
            print(f"{name:14s} seed {'FAIL (good)' if r.returncode != 0 else 'PASS (BAD: seed should not pass)'}")
            bad += r.returncode == 0
            shutil.rmtree(sb2, ignore_errors=True)
        shutil.rmtree(sb, ignore_errors=True)
    print("selftest", "OK" if not bad else f"{bad} problems")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
