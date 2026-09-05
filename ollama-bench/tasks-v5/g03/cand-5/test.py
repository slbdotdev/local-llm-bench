import ast
import hashlib
import importlib
import inspect
import os
import sys
import threading

_ORA_TOTAL = 14
_ora_done = 0
_ora_fails = []
_ora_import_ok = False
_ora_core = None
_ora_registry = None
_ora_lock = threading.Lock()


def _ora_watchdog():
    score = max(0, min(_ORA_TOTAL, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    print("FAIL ['grader timed out']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_check(name, function):
    global _ora_done
    try:
        ok = bool(function())
    except Exception:
        ok = False
    if not ok:
        _ora_fails.append(name)
    with _ora_lock:
        _ora_done += 1


def _ora_source_files():
    paths = []
    root = os.path.join(os.getcwd(), "badges")
    for folder, dirs, files in os.walk(root):
        dirs.sort()
        for filename in sorted(files):
            if filename.endswith(".py"):
                paths.append(os.path.join(folder, filename))
    return paths


def _ora_no_old_name():
    return all("make_tag" not in open(path, encoding="utf-8").read()
               for path in _ora_source_files())


def _ora_signature():
    params = inspect.signature(_ora_core.make_badge).parameters
    return (list(params) == ["label", "tone"] and
            params["tone"].kind is inspect.Parameter.KEYWORD_ONLY and
            params["tone"].default == "plain")


def _ora_positional_rejected():
    try:
        _ora_core.make_badge("A", "warm")
    except TypeError:
        return True
    return False


def _ora_compile_all():
    return all(compile(open(path, encoding="utf-8").read(), path, "exec")
               for path in _ora_source_files())


def _ora_import_all():
    for path in _ora_source_files():
        relative = os.path.relpath(path, os.getcwd())[:-3].replace(os.sep, ".")
        if relative.endswith(".__init__"):
            relative = relative[:-9]
        importlib.import_module(relative)
    return True


def _ora_order():
    path = os.path.join(os.getcwd(), "badges", "core.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    expected = ["make_badge", "batch", "normalize", "make_normalized",
                "is_known_tone", "grouped", "labeled", "describe"]
    return names == expected


def _ora_candidate_worked():
    return _ora_import_ok and callable(getattr(_ora_core, "make_badge", None))


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()
sys.path.insert(0, os.getcwd())
try:
    try:
        import badges.core as _ora_core
        import badges.registry as _ora_registry
        _ora_import_ok = True
    except Exception:
        _ora_import_ok = False

    if _ora_import_ok:
        _ora_check("new symbol", lambda: callable(_ora_core.make_badge))
        _ora_check("old name absent", _ora_no_old_name)
        _ora_check("keyword-only signature", _ora_signature)
        _ora_check("direct output", lambda: _ora_core.make_badge("Ada", tone="warm") == "Ada<warm>")
        _ora_check("positional tone rejected", _ora_positional_rejected)
        _ora_check("default and batch", lambda: _ora_core.batch(["A", "B"], tone="cool") == ["A<cool>", "B<cool>"])
        _ora_check("flow and formatting", lambda: __import__("badges.flow", fromlist=["decorate"]).decorate("Q", tone="red") == "Q<red>")
        _ora_check("reflection", lambda: _ora_registry.reflect("R", tone="gold") == "R<gold>")
        _ora_check("package export", lambda: __import__("badges", fromlist=["make_badge"]).make_badge("Z") == "Z<plain>")
        _ora_check("all sources compile", _ora_compile_all)
        _ora_check("all modules import", _ora_import_all)
        _ora_check("pipeline integration", lambda: __import__("badges.pipeline", fromlist=["pipeline_text"]).pipeline_text(["A", "B"], tone="muted") == "A<muted>\nB<muted>")
        _ora_check("definition order", _ora_order)
        _ora_check("registry default", lambda: _ora_registry.resolve()("S", tone="silver") == "S<silver>")
    else:
        _ora_fails.extend(["import"] + ["not run"] * (_ORA_TOTAL - 1))
        _ora_done = _ORA_TOTAL

    score = max(0, min(_ORA_TOTAL, _ORA_TOTAL - len(_ora_fails)))
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    if score == _ORA_TOTAL:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL", _ora_fails[:10])
    print("VERDICT %s" % ("confidently_wrong" if _ora_candidate_worked() else "visibly_failed"))
    sys.exit(1)
finally:
    _timer.cancel()
