"""g04/cand-5 labelled an untouched sandbox `confidently_wrong`. It must be `visibly_failed`.

CONTRACT.md is explicit: `confidently_wrong` is for an answer that is wrong AND is a confident
positive assertion; `visibly_failed` covers "crashed, refused, produced nothing, ... left the
required artifact absent". A model that changed nothing produced nothing.

The mechanism: the checker decides `confidently_wrong` whenever the target module imports and a
behaviour subcheck fails. The pristine seed module imports fine and fails those subchecks by
construction, so doing nothing scored as a confident wrong answer. Since the confidently-wrong
rate is the campaign's headline instrument and outranks pass rate (plan section 6), every
did-nothing trial would have inflated the headline number for every quant.

The fix is the one the rest of the suite already uses: hard-code the pristine digest of the file
the task is supposed to change, and force `visibly_failed` when it is untouched.

**This makes the digest stale if `seed/src/reconcile.py` is ever edited.** Re-run this script
after any such edit, and re-run `verify_candidates.py` immediately before taking any hashes.

Usage:  python3 fix_g04c5_empty_verdict.py
"""
import hashlib, os

CAND = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "tasks-v5", "g04", "cand-5"))
TARGET_REL = "src/reconcile.py"
MARK = "_ORA_PRISTINE_TARGET"

OLD = '''            verdict = ("confidently_wrong" if _ora_mod_ready and _ora_behavior_failed
                       else "visibly_failed")'''
NEW = '''            # A sandbox whose target file is byte-identical to the pristine seed produced
            # NOTHING, so it is visibly_failed however the behaviour subchecks land. Without
            # this, doing nothing scores `confidently_wrong` -- and that is the campaign's
            # headline instrument, which outranks pass rate.
            verdict = ("confidently_wrong"
                       if _ora_mod_ready and _ora_behavior_failed and not _ora_untouched()
                       else "visibly_failed")'''

HELPER = '''

_ORA_PRISTINE_TARGET = "{digest}"


def _ora_untouched():
    """True when the file the task must change is byte-identical to the pristine seed."""
    try:
        with open("{target}", "rb") as _fh:
            return hashlib.sha256(_fh.read()).hexdigest() == _ORA_PRISTINE_TARGET
    except Exception:
        return False

'''


def main():
    target = os.path.join(CAND, "seed", TARGET_REL)
    digest = hashlib.sha256(open(target, "rb").read()).hexdigest()
    p = os.path.join(CAND, "test.py")
    src = open(p, encoding="utf-8").read()
    if MARK in src:
        print("already patched")
        return
    if "import hashlib" not in src:
        src = src.replace("import ", "import hashlib\nimport ", 1)
    assert OLD in src, "verdict block not found"
    src = src.replace(OLD, NEW, 1)
    anchor = "def _ora_report("
    src = src.replace(anchor, HELPER.format(digest=digest, target=TARGET_REL) + anchor, 1)
    open(p, "w", encoding="utf-8").write(src)
    print(f"patched; pristine digest {digest[:16]}...")


if __name__ == "__main__":
    main()
