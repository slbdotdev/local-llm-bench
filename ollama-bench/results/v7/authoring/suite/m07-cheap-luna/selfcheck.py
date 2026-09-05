import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile


BASE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(BASE, "seed")
GRADER = os.path.join(BASE, "test.py")
REF_PATH = os.path.join(BASE, "ref", "solve.py")


def reference():
    spec = importlib.util.spec_from_file_location("m07_reference", REF_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.apply


def run_case(parent, name, mutate=None, reference_answer=True):
    case = os.path.join(parent, name)
    shutil.copytree(SEED, case)
    shutil.copyfile(GRADER, os.path.join(case, "test.py"))
    if reference_answer:
        reference()(case)
    if mutate:
        mutate(case)
    result = subprocess.run([sys.executable, os.path.join(case, "test.py")], cwd=case,
                            capture_output=True, text=True, encoding="utf-8", timeout=10)
    for line in result.stdout.splitlines():
        if line.startswith("VERDICT "):
            return line
    return "NO VERDICT"


def watermark_source(case):
    return os.path.join(case, "src", "prism", "watermark_view.py")


def tweak(case, action):
    path = watermark_source(case)
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    if action == "none":
        text = text[:-1] if text.endswith("\n") else text
    elif action == "double":
        text += "\n"
    elif action == "crlf":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    elif action == "leading":
        text = "\n" + text
    elif action == "spaces":
        text = text.replace("def load_watermark", "def  load_watermark", 1)
    elif action == "order":
        path = os.path.join(case, "config", "pipeline_templates.json")
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        ordered = {"owner_note": data["owner_note"], "arguments": data["arguments"],
                   "factory": data["factory"], "job_kind": data["job_kind"]}
        text = json.dumps(ordered, indent=2) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def wrong_partial(case):
    for base, dirs, names in os.walk(case):
        for name in names:
            path = os.path.join(base, name)
            if path == os.path.join(case, "config", "pipeline_templates.json"):
                continue
            with open(path, "r", encoding="utf-8", newline="") as handle:
                text = handle.read()
            if "build_watermark" in text:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    handle.write(text.replace("build_watermark", "load_watermark"))


def main():
    parent = tempfile.mkdtemp(prefix="m07-probe-", dir=BASE)
    try:
        outcomes = [run_case(parent, "reference")]
        for action in ("none", "double", "crlf", "leading", "spaces", "order"):
            outcomes.append(run_case(parent, action,
                                     lambda case, a=action: tweak(case, a)))
        outcomes.append(run_case(parent, "wrong", wrong_partial, reference_answer=False))
        outcomes.append(run_case(parent, "untouched", reference_answer=False))
        print("; ".join(outcomes))
    finally:
        shutil.rmtree(parent)


if __name__ == "__main__":
    main()
