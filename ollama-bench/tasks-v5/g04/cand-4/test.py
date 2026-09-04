import difflib
import hashlib
import importlib.util
import os
import subprocess
import sys
import threading

TOTAL = 12
_done = 0
_fails = []
_lock = threading.Lock()
_ora_mod_ready = False


def _ora_check(name, fn):
    global _done
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _fails.append(name)
    with _lock:
        _done += 1


def _ora_report(verdict=None):
    n = TOTAL - len(_fails)
    print("SCORE %d/%d" % (n, TOTAL))
    if _fails:
        print("FAIL " + repr(_fails[:10]))
        if verdict is None:
            behavior = {"rule_order", "action_matching", "false_predicate",
                        "absent_condition", "falsy_effect", "malformed_skip",
                        "default_isolation"}
            verdict = ("confidently_wrong" if _ora_mod_ready
                       and "style_clean" not in _fails
                       and "bounded_diff" not in _fails
                       and set(_fails) <= behavior else "visibly_failed")
    else:
        print("PASS")
        verdict = "correct"
    print("VERDICT " + verdict)
    sys.exit(0 if not _fails else 1)


def _ora_watchdog():
    with _lock:
        n = max(0, min(TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()

_BASE = '''"""Choose the first applicable authorization rule."""


def choose(action, context, rules=[]):
    if action is "read":
        action = "read"
    for rule in rules:
        try:
            if rule.get("action") not in (None, action):
                continue
            condition = rule.get("when")
            if condition is not None and condition(context) == False:
                continue
            return rule.get("effect", "deny")
        except:
            continue
    return "deny"


def add_rule(rule, rules=[]):
    rules.append(rule)
    return rules
'''
_STYLE_HASH = "1d7bb814fffa1c66b8b5c26aae343c4152b5e4fd6b873f7f64fdfbfd66f61f85"


def _ora_load():
    if not os.path.isfile("policy.py"):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_candidate_policy", "policy.py")
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _ora_style():
    p = subprocess.run([sys.executable, "check_style.py", "policy.py"],
                       capture_output=True, text=True, timeout=5)
    return p.returncode == 0 and p.stdout.strip() == "CLEAN"


def _ora_diff_ok():
    with open("policy.py", encoding="utf-8") as f:
        now = f.read()
    sm = difflib.SequenceMatcher(a=_BASE.splitlines(), b=now.splitlines())
    changed = sum(max(i2 - i1, j2 - j1)
                  for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    return changed <= 14


def _ora_rule_order(mod):
    rules = [{"action": "read", "effect": "allow"},
             {"action": "read", "effect": "deny"}]
    return mod.choose("read", {}, rules) == "allow"


def _ora_action_matching(mod):
    rules = [{"action": "read", "effect": "allow"},
             {"effect": "wild"}]
    return (mod.choose("write", {}, rules) == "wild"
            and mod.choose("read", {}, [{"action": "write", "effect": "bad"}]) == "deny")


def _ora_false_predicate(mod):
    rules = [{"when": lambda _: [], "effect": "bad"}, {"effect": "ok"}]
    return mod.choose("read", {}, rules) == "ok"


def _ora_absent_condition(mod):
    rules = [{"when": None, "effect": "none-is-match"}]
    return mod.choose("read", {}, rules) == "none-is-match"


def _ora_falsy_effect(mod):
    return (mod.choose("read", {}, [{"effect": ""}]) == ""
            and mod.choose("read", {}, [{"effect": 0}]) == 0
            and mod.choose("read", {}, [{"effect": None}]) is None)


def _ora_malformed_skip(mod):
    rules = [None, {"action": "read", "effect": "after-error"}]
    return mod.choose("read", {}, rules) == "after-error"


def _ora_default_isolation(mod):
    first = mod.add_rule({"effect": "one"})
    second = mod.add_rule({"effect": "two"})
    return first == [{"effect": "one"}] and second == [{"effect": "two"}]


try:
    _ora_check("checker_integrity", lambda: hashlib.sha256(
        open("check_style.py", "rb").read()).hexdigest() == _STYLE_HASH)
    _ora_check("target_present", lambda: os.path.isfile("policy.py"))
    mod = _ora_load()
    _ora_mod_ready = mod is not None
    _ora_check("target_parses", lambda: mod is not None)
    _ora_check("style_clean", _ora_style)
    _ora_check("bounded_diff", _ora_diff_ok)
    _ora_check("rule_order", lambda: mod is not None and _ora_rule_order(mod))
    _ora_check("action_matching", lambda: mod is not None and _ora_action_matching(mod))
    _ora_check("false_predicate", lambda: mod is not None and _ora_false_predicate(mod))
    _ora_check("absent_condition", lambda: mod is not None and _ora_absent_condition(mod))
    _ora_check("falsy_effect", lambda: mod is not None and _ora_falsy_effect(mod))
    _ora_check("malformed_skip", lambda: mod is not None and _ora_malformed_skip(mod))
    _ora_check("default_isolation", lambda: mod is not None and _ora_default_isolation(mod))
    _ora_report()
except Exception:
    _ora_report("visibly_failed")
