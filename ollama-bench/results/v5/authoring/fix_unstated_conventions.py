"""Two more unstated conventions, both found by running a reference model and reading why it
failed rather than by assuming the failure was difficulty.

plan-2026-09-05 section 2.3: ambiguity, unstated conventions and trick wording are never on
the difficulty ladder. A tighter output contract is a legitimate lever only where the contract
is STATED EXACTLY and is checkable. Both of these were checkable and neither was stated.

(1) t03/cand-1 -- verbatim copying was required but never stated.
    Its checker accepts exactly one string for `impact_scope`:
    "delayed telemetry writes for 12.4% of eu-west-2 tenants". A trial answered
    "delayed telemetry writes AFFECTING 12.4% of eu-west-2 tenants" -- a paraphrase that
    preserves the meaning, which is all the prompt asked for -- and the shape gate then
    zeroed all eight fields. The prompt is made exact; the checker stays strict.

(2) t04/cand-1 -- the explanation check matched literal word forms, not the concept.
    Its groups required the substring "expired" or "expiry". A trial wrote "when the
    session's expires_at has passed", which names the expiry decision exactly as the prompt
    asks, and failed on the word form alone. Matching is moved to stems, so every inflection
    of the same concept counts. This is a checker fix: the prompt already stated the
    requirement correctly.

Usage:  python3 fix_unstated_conventions.py t03 <prompt.md> | t04 <test.py>
"""
import sys

T03_ANCHOR = ("Use the value supported by the authoritative record, not a nearby estimate, "
              "proposal,\nor example.")
T03_ADD = (" Copy each string value **verbatim** from that record -- its exact\n"
           "wording, spelling and punctuation, not a paraphrase or a reworded summary.")
T03_MARK = "Copy each string value **verbatim**"

T04_OLD = '''    groups = (
        ("expired", "expiry"),
        ("unauthenticated", "unauthorized", "401"),
        ("cookie",),
        ("remove", "clear", "cleared", "delete"),
    )'''
T04_NEW = '''    # Stems, not word forms. The prompt asks the explanation to "mention the expiry
    # decision, the unauthenticated response, and the cookie removal" -- it says nothing
    # about which inflection to use, so requiring the literal "expired" or "expiry"
    # scored a correct explanation ("when the session's expires_at has passed") as wrong.
    groups = (
        ("expir",),
        ("unauthenticated", "unauthorized", "401"),
        ("cookie",),
        ("remov", "clear", "delet", "unset", "drop"),
    )'''
T04_MARK = "Stems, not word forms"


def patch(kind, path):
    src = open(path, encoding="utf-8").read()
    mark, old, new = ((T03_MARK, T03_ANCHOR, T03_ANCHOR + T03_ADD) if kind == "t03"
                      else (T04_MARK, T04_OLD, T04_NEW))
    if mark in src:
        print(f"{path}: already patched")
        return 0
    if old not in src:
        print(f"{path}: NO MATCH -- inspect by hand")
        return -1
    open(path, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print(f"{path}: patched ({kind})")
    return 1


if __name__ == "__main__":
    kind = sys.argv[1]
    bad = sum(1 for p in sys.argv[2:] if patch(kind, p) < 0)
    sys.exit(1 if bad else 0)
