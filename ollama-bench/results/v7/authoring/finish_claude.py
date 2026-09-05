#!/usr/bin/env python3
"""Revision round for the Claude family, applying the Luna review in reviews/luna-reviews-claude.md.

    python3 finish_claude.py

Run AFTER build_claude_main.py, build_claude_main_b.py and build_claude_cheap.py, which it
patches in place. Everything here is a review finding, not a second thought:

  all seven   `selfcheck.py` was missing entirely, and MANIFEST.json carried no measured
              material fields. Both are required by AUTHORING-BRIEF.md sections 3 and 5.
  m01         no subcheck covered the prompt's stated rule that an unknown key is ignored.
  m04         the grader stripped the first line of report.txt, accepting trailing spaces,
              while rejecting a leading blank line — strict and lenient about the same stated
              rule. The prompt says the line must be EXACTLY one of two strings, so both are
              now rejected.
  m06         only tests/test_budget.py was hashed, so another test file could be edited freely.
              Every seed file under tests/ is now hashed.
  m07         the stale-name scan matched the lowercase stage name and the class name, but not
              the UPPERCASE module constants the prompt explicitly requires renamed, so
              DEFAULT_<OLD>_LIMIT could survive and still score 9/9.
  m10         the grader normalised CRLF although the prompt expressly requires LF, and rejected
              an extra trailing newline the prompt does not forbid. Line endings are now checked
              as raw bytes, against what the prompt actually states.
  m09         blank lines were dropped before counting, so a four-line answer passed a
              two-line contract.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cand-claude")
CHARS_PER_TOKEN = 4.664

SELFCHECK = '''#!/usr/bin/env python3
"""Execute this task's prompt examples against ref/, and confirm the reference is correct.

    python3 selfcheck.py

Required by AUTHORING-BRIEF.md section 3. It is deliberately NOT the same instrument as
test.py: the grader asks "is this answer right", and this asks "does the reference actually
satisfy every example the prompt shows a reader". A prompt whose worked example disagrees with
its own reference is the defect this catches, and it has occurred in this benchmark before.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def build():
    sb = tempfile.mkdtemp(prefix="selfcheck-")
    shutil.copytree(os.path.join(HERE, "seed"), sb, dirs_exist_ok=True)
    ref = os.path.join(HERE, "ref")
    if os.path.isdir(ref):
        shutil.copytree(ref, sb, dirs_exist_ok=True)
    solve = os.path.join(sb, "solve.py")
    if os.path.exists(solve):
        subprocess.run([sys.executable, "solve.py"], cwd=sb, check=True,
                       env=dict(os.environ, PYTHONUTF8="1"), capture_output=True)
        os.remove(solve)
    return sb


def grade(sb):
    shutil.copy(os.path.join(HERE, "test.py"), os.path.join(sb, "_hidden_test.py"))
    p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.stdout, p.returncode


def main():
    sb = build()
    out, rc = grade(sb)
    problems = []
    if "PASS" not in out or rc != 0:
        problems.append("the reference does not pass its own grader: %r" % out.strip()[-200:])
    if "VERDICT correct" not in out:
        problems.append("the reference is not graded `correct`")
    m = re.search(r"SCORE (\\d+)/(\\d+)", out)
    if not m or m.group(1) != m.group(2):
        problems.append("the reference does not score full marks: %s" % (m.group(0) if m else "no SCORE"))
%(extra)s
    shutil.rmtree(sb, ignore_errors=True)
    if problems:
        print("SELFCHECK FAILED")
        for p in problems:
            print("  - " + p)
        return 1
    print("selfcheck ok: reference scores %s, VERDICT correct, and every prompt example holds"
          % m.group(0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

EXTRA = {
    "m01-main-claude": '''
    # the prompt states: "A key in `ages` that the stage has never seen is ignored" and
    # "calling `reap` twice with the same argument reaps nothing the second time".
    import importlib
    import json as _json
    sys.path.insert(0, os.path.join(sb, "src"))
    man = _json.load(open(os.path.join(sb, "config", "manifest.json"), encoding="utf-8"))
    st = man["stages"][0]
    mod = importlib.import_module(man["package"] + "." + st["module"])
    eng = getattr(mod, st["class"])()
    if eng.reap({"never-seen": 10 ** 6}) != 0:
        problems.append("prompt example: an unknown key must be ignored, and is not")
''',
    "m04-main-claude": '''
    # the prompt fixes the first line of report.txt to exactly one of two strings.
    with open(os.path.join(sb, "report.txt"), encoding="utf-8") as fh:
        first = fh.read().split("\\n")[0]
    if first not in ("TESTS: pass", "TESTS: fail"):
        problems.append("prompt example: report.txt's first line is %r" % first)
''',
    "m07-main-claude": '''
    # the prompt requires the renamed constants and factory to exist.
    import importlib
    sys.path.insert(0, os.path.join(sb, "src"))
''',
    "m10-main-claude": '''
    # the prompt fixes the header and the ordering; check the artifact against the prompt.
    with open(os.path.join(sb, "report", "limits.csv"), "rb") as fh:
        raw = fh.read()
    if b"\\r\\n" in raw:
        problems.append("prompt example: the CSV must use LF line endings")
    lines = raw.decode("utf-8").split("\\n")
    if lines[0] != "stage,limit,window_s":
        problems.append("prompt example: header is %r" % lines[0])
    rows = [ln for ln in lines[1:] if ln]
    keys = [(-int(r.split(",")[1]), r.split(",")[0]) for r in rows]
    if keys != sorted(keys):
        problems.append("prompt example: rows are not sorted by limit desc then name asc")
''',
    "m03-cheap-claude": '''
    # docs/rounding.md's worked table: 0.4->0, 0.5->1, 1.5->2, 2.5->3
    import importlib
    import json as _json
    sys.path.insert(0, os.path.join(sb, "src"))
    man = _json.load(open(os.path.join(sb, "config", "manifest.json"), encoding="utf-8"))
    rates = importlib.import_module(man["package"] + ".rates")
    for value, want in ((0.4, 0), (0.5, 1), (1.5, 2), (2.5, 3)):
        if rates.round_half_up(value) != want:
            problems.append("documented example round_half_up(%s) should be %d" % (value, want))
''',
    "m06-cheap-claude": '''
    # docs/budget.md's worked table: remaining(3,10)->7, (10,10)->0, (12,10)->0
    import importlib
    import json as _json
    sys.path.insert(0, os.path.join(sb, "src"))
    man = _json.load(open(os.path.join(sb, "config", "manifest.json"), encoding="utf-8"))
    budget = importlib.import_module(man["package"] + ".budget")
    for args, want in (((3, 10), 7), ((10, 10), 0), ((12, 10), 0)):
        if budget.remaining(*args) != want:
            problems.append("documented example remaining%r should be %d" % (args, want))
''',
    "m09-cheap-claude": '''
    # the prompt fixes the answer to exactly two lines, and the slot with no leading zeros.
    with open(os.path.join(sb, "answer.txt"), encoding="utf-8") as fh:
        lines = fh.read().rstrip("\\n").split("\\n")
    if len(lines) != 2:
        problems.append("prompt example: answer.txt must have exactly two lines, has %d"
                        % len(lines))
    if not re.fullmatch(r"SLOT: [1-9]\\d*", lines[-1]):
        problems.append("prompt example: slot line is %r, must have no leading zeros"
                        % lines[-1])
''',
}


def measure(seed):
    chars = files = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".pytest_cache")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            with open(os.path.join(base, n), encoding="utf-8") as fh:
                chars += len(fh.read())
            files += 1
    return files, chars


def patch(path, old, new, why):
    src = open(path, encoding="utf-8").read()
    if old not in src:
        print("  !! could not apply (%s): pattern absent in %s" % (why, os.path.basename(path)))
        return False
    open(path, "w", encoding="utf-8", newline="\n").write(src.replace(old, new, 1))
    print("  -- %s" % why)
    return True


def main():
    for slot in sorted(os.listdir(OUT)):
        cand = os.path.join(OUT, slot)
        if not os.path.isdir(os.path.join(cand, "seed")):
            continue
        print(slot)

        # 1. selfcheck.py, missing on all seven
        open(os.path.join(cand, "selfcheck.py"), "w", encoding="utf-8", newline="\n").write(
            SELFCHECK.replace("%(extra)s", EXTRA.get(slot, "")))
        print("  -- wrote selfcheck.py")

        # 2. MANIFEST.json measured fields, missing on all seven
        mp = os.path.join(cand, "MANIFEST.json")
        man = json.load(open(mp, encoding="utf-8"))
        files, chars = measure(os.path.join(cand, "seed"))
        man.update({"material_chars": chars,
                    "material_tokens": int(round(chars / CHARS_PER_TOKEN)),
                    "seed_files": files})
        open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(man, indent=1) + "\n")
        print("  -- MANIFEST.json: %d files, %d chars, %d tokens"
              % (files, chars, man["material_tokens"]))

        t = os.path.join(cand, "test.py")

        if slot == "m01-main-claude":
            patch(t, '_ora_total = 12', '_ora_total = 13',
                  "one more subcheck")
            patch(t, '''    _ora_check("reaping twice reaps nothing the second time", _idempotent)''',
                  '''    _ora_check("reaping twice reaps nothing the second time", _idempotent)

    def _unknown_key():
        e, _ = _fresh()
        return e.reap({"never-seen": 10 ** 6}) == 0 and len(e.snapshot()) == 4
    _ora_check("a key the stage has never seen is ignored", _unknown_key)''',
                  "cover the prompt's stated unknown-key rule")
            patch(t, '''    for _n in range(12):''', '''    for _n in range(13):''',
                  "keep the not-implemented branch in step with the total")

        if slot == "m04-main-claude":
            patch(t, '''            _first = _fh.read().replace("\\r\\n", "\\n").split("\\n")[0].strip()''',
                  '''            # The prompt says the FIRST LINE must be exactly one of two strings.
            # So a trailing space is a violation of a stated rule, exactly as a leading
            # blank line is; the grader must not be strict about one and lenient about the
            # other. CRLF and a BOM are still normalised, because the prompt is silent
            # about those.
            _first = _fh.read().replace("\\r\\n", "\\n").split("\\n")[0]''',
                  "stop stripping the exactly-specified first line")

        if slot == "m06-cheap-claude":
            patch(t, 'def _test_file_untouched():\n    return os.path.exists(TEST_PATH) and _sha(TEST_PATH) == TEST_SHA',
                  '''SEED_TEST_SHAS = %r


def _test_file_untouched():
    """Every seed file under tests/ must survive byte-identically, not only the one that fails.

    Hashing only test_budget.py left every other test file editable, which is the same
    escape route by a different door.
    """
    for rel, want in SEED_TEST_SHAS.items():
        p = os.path.join("tests", rel)
        if not os.path.exists(p) or _sha(p) != want:
            return False
    return True''' % _test_shas(cand),
                  "hash every seed file under tests/, not only the failing one")

        if slot == "m07-main-claude":
            patch(t, '''                if OLD in body or OLDCLS in body or OLD in n:''',
                  '''                # The prompt requires the UPPERCASE module constants renamed too, so
                # the scan has to look for them. Matching only the lowercase stage name
                # let DEFAULT_<OLD>_LIMIT survive at a full score.
                if (OLD in body or OLDCLS in body or OLD.upper() in body
                        or OLD in n or OLD.upper() in n):''',
                  "scan for the uppercase constants the prompt names")

        if slot == "m09-cheap-claude":
            patch(t, '''    return [ln.strip() for ln in text.strip("\\n").split("\\n") if ln.strip()]''',
                  '''    # Blank lines are NOT dropped: the prompt fixes the file at exactly two lines,
    # so a four-line answer must not pass a two-line contract.
    return [ln.strip() for ln in text.strip("\\n").split("\\n")]''',
                  "stop dropping blank lines from a two-line contract")

        if slot == "m10-main-claude":
            patch(t, '''def _read(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8-sig").replace("\\r\\n", "\\n")''',
                  '''def _read(path):
    """Decode without normalising line endings.

    The prompt states LF line endings in terms, so silently accepting CRLF was a false
    acceptance of a stated rule. A BOM is still tolerated: the prompt is silent about it.
    """
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8-sig")


def _lf_only(path):
    with open(path, "rb") as fh:
        return b"\\r" not in fh.read()''',
                  "check LF as bytes rather than normalising CRLF away")
            patch(t, '''_ora_check("the CSV ends with a final newline",
           lambda: _csv_present and _read(CSV).endswith("\\n"))''',
                  '''_ora_check("the CSV ends with a final newline",
           lambda: _csv_present and _read(CSV).endswith("\\n"))
_ora_check("the CSV uses the LF line endings the prompt requires",
           lambda: _csv_present and _lf_only(CSV))''',
                  "add the LF subcheck the prompt's own rule implies")
            patch(t, '_ora_total = 8', '_ora_total = 9', "one more subcheck")

    print("\nrebuild nothing; re-run probe_candidate.py and selfcheck.py on all seven")


def _test_shas(cand):
    import hashlib
    out = {}
    tdir = os.path.join(cand, "seed", "tests")
    for n in sorted(os.listdir(tdir)):
        if n.endswith(".py"):
            with open(os.path.join(tdir, n), "rb") as fh:
                out[n] = hashlib.sha256(fh.read()).hexdigest()
    return out


if __name__ == "__main__":
    main()
