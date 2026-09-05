import json
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def finish(score, verdict):
    print("SCORE %d/1" % score)
    if score == 1 and verdict == "correct":
        print("PASS")
    print("VERDICT %s" % verdict)
    raise SystemExit(0 if score == 1 and verdict == "correct" else 1)


def main():
    root = os.getcwd()
    sys.path.insert(0, os.path.join(root, "src"))
    from prism.watermark_view import WatermarkEngine, load_watermark
    module_text = read_text(os.path.join(root, "src", "prism", "watermark_view.py"))
    config_path = os.path.join(root, "config", "pipeline_templates.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    old_name = "build_" + "watermark"
    old_exists = False
    for base, dirs, names in os.walk(root):
        dirs[:] = [item for item in dirs if item not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        for name in names:
            if name.endswith((".pyc", ".pyo")):
                continue
            path = os.path.join(base, name)
            with open(path, "r", encoding="utf-8") as handle:
                old_exists = old_exists or old_name in handle.read()
    engine = load_watermark({"watermark": {"limit": 7}})
    correct = (isinstance(engine, WatermarkEngine) and engine.limit == 7
               and config.get("factory") == "load_watermark"
               and callable(load_watermark) and not old_exists)
    if correct:
        finish(1, "correct")
    finish(0, "confidently_wrong" if "load_watermark" in module_text else "visibly_failed")


try:
    main()
except SystemExit:
    raise
except Exception:
    finish(0, "visibly_failed")
