import importlib.util
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
    spec = importlib.util.spec_from_file_location("m01_reference", REF_PATH)
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


def tweak(path, action):
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
        text = text.replace("return [self._slots[k]", "return  [self._slots[k]", 1)
    elif action == "order":
        text = text.replace("reversed(sorted(self._slots))", "sorted(self._slots)")
    elif action == "wrong":
        text = text.replace("reversed(sorted(self._slots))", "list(reversed(self._slots))")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main():
    parent = tempfile.mkdtemp(prefix="m01-probe-", dir=BASE)
    source = os.path.join("src", "harbor", "schema_store.py")
    try:
        outcomes = [run_case(parent, "reference")]
        for action in ("none", "double", "crlf", "leading", "spaces"):
            outcomes.append(run_case(parent, action,
                                     lambda case, a=action: tweak(os.path.join(case, source), a)))
        outcomes.append(run_case(parent, "ordering",
                                 lambda case: tweak(os.path.join(case, source), "order")))
        outcomes.append(run_case(parent, "wrong",
                                 lambda case: tweak(os.path.join(case, source), "wrong"),
                                 reference_answer=True))
        outcomes.append(run_case(parent, "untouched", reference_answer=False))
        print("; ".join(outcomes))
    finally:
        shutil.rmtree(parent)


if __name__ == "__main__":
    main()
