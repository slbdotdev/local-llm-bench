"""Assert that every value a reference answer asserts is actually PRESENT in the material.

The defect this exists for. t03/cand-1 is an extraction task: read a long technical record,
report eight fields. Its reference answer gives `incident_date` as "2031-04-17". The string
"2031-04-17" does not appear in its seed material. Neither does "2031". Neither does any ISO
date at all. The task is unanswerable on that field, and its prompt explicitly forbids
inferring: "Do not infer or calculate facts that are not stated there."

Two reference models answered `null` for it -- correctly, on the material they were given --
and were both scored `visibly_failed` with SCORE 0/8, because one non-string value trips the
checker's shape gate and zeroes every other field.

plan-2026-09-05 section 2.3 bans missing information from the difficulty ladder outright. This
is missing information, and it is the most expensive kind: it looks exactly like a hard task.

Why nothing already in the tree could catch it. `verify_candidates.py` copies `ref/` into the
sandbox and runs the checker, so the reference passes by construction whatever it asserts --
it never asks whether the material supports the assertion. `probe_checkers.py` perturbs a
correct answer, so it inherits the same blind spot. `selfcheck.py` executes the prompt's
examples against `ref/`, not against `seed/`. All three agree with each other and all three
are wrong together.

Method. For each candidate with a JSON reference answer, take every leaf string and number,
normalise whitespace and case, and search the concatenated seed material for it. Also try a
few tolerant forms, because a record may legitimately write a number with separators or a
date in another format. Anything not found is reported for a human read: this is a
strong hint, not a verdict, because a legitimate answer can be a paraphrase the prompt asked
for or a value assembled from parts.

  python3 check_derivable.py [<tasks-dir>]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "tasks-v5"))
SKIP_DIRS = {"__pycache__", ".git"}


def seed_text(cand):
    parts = []
    seed = os.path.join(cand, "seed")
    for root, dirs, files in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                continue
            try:
                parts.append(open(os.path.join(root, f), encoding="utf-8").read())
            except (UnicodeDecodeError, OSError):
                pass
    return "\n".join(parts)


def leaves(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{path}[{i}]")
    elif obj is not None and not isinstance(obj, bool):
        yield path, obj


def present(value, hay_norm, hay_raw):
    """Tolerant containment: exact, whitespace-normalised, and a few number/date forms."""
    s = str(value).strip()
    if not s:
        return True
    if s in hay_raw:
        return True
    norm = re.sub(r"\s+", " ", s).casefold()
    if norm in hay_norm:
        return True
    if isinstance(value, (int, float)):
        for alt in (f"{value:,}", str(value).rstrip("0").rstrip("."),
                    re.sub(r"\B(?=(\d{3})+(?!\d))", " ", str(value))):
            if alt and alt.casefold() in hay_norm:
                return True
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = m.groups()
        # Only whole-date alternates. An earlier version also accepted the bare year and
        # the bare day-of-month, which matches almost any prose and made the check pass a
        # date that was genuinely absent -- a tolerant check that tolerates everything is
        # worse than none, because it reads as a clean result.
        month = ("january february march april may june july august september october "
                 "november december").split()[int(mo) - 1]
        for alt in (f"{y}/{mo}/{d}", f"{d}/{mo}/{y}", f"{mo}/{d}/{y}",
                    f"{int(d)} {month[:3]} {y}", f"{month} {int(d)}, {y}",
                    f"{int(d)} {month} {y}"):
            if alt.casefold() in hay_norm:
                return True
    return False


def main():
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    problems = []
    checked = 0
    for tid in sorted(os.listdir(root)):
        tdir = os.path.join(root, tid)
        if not os.path.isdir(tdir):
            continue
        cands = [c for c in sorted(os.listdir(tdir))
                 if os.path.isdir(os.path.join(tdir, c))]
        for cn in cands or [""]:
            cand = os.path.join(tdir, cn) if cn else tdir
            refd = os.path.join(cand, "ref")
            if not os.path.isdir(refd):
                continue
            jsons = [f for f in os.listdir(refd) if f.endswith(".json")]
            if not jsons:
                continue
            hay_raw = seed_text(cand)
            hay_norm = re.sub(r"\s+", " ", hay_raw).casefold()
            for j in jsons:
                try:
                    obj = json.load(open(os.path.join(refd, j), encoding="utf-8"))
                except Exception as e:
                    problems.append(f"{tid}/{cn}: {j} unreadable ({e})")
                    continue
                checked += 1
                missing = [(p, v) for p, v in leaves(obj)
                           if not present(v, hay_norm, hay_raw)]
                name = f"{tid}/{cn}" if cn else tid
                if missing:
                    for p, v in missing:
                        problems.append(f"{name}: {j} asserts {p}={v!r}, "
                                        f"not found in seed material")
                    print(f"{name:16s} {j:14s} NOT DERIVABLE: "
                          + ", ".join(p for p, _ in missing), flush=True)
                else:
                    print(f"{name:16s} {j:14s} all values present in seed", flush=True)
    print("\n=== summary ===")
    print(f"json reference answers checked: {checked}")
    if problems:
        print(f"{len(problems)} values not found in the material:")
        for p in problems:
            print("  -", p)
        print("\nEach needs a human read: a value may legitimately be a paraphrase the prompt\n"
              "asked for, or assembled from parts. A value that is simply absent is a broken task.")
    else:
        print("every asserted value appears in the material")


if __name__ == "__main__":
    main()
