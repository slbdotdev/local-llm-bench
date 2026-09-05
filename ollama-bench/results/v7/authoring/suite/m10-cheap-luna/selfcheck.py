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
    spec = importlib.util.spec_from_file_location("m10_reference", REF_PATH)
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


def tweak(case, action):
    path = os.path.join(case, "config", "formatting.ini")
    with open(path, "rb") as handle:
        data = handle.read()
    if action == "none":
        data = data[:-2] if data.endswith(b"\r\n") else data
    elif action == "double":
        data += b"\r\n"
    elif action == "crlf":
        data = data.replace(b"\n", b"\r\n") if b"\r\n" not in data else data
    elif action == "leading":
        data = b"\r\n" + data
    elif action == "spaces":
        data = data.replace(b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo \xe2\x80\x94 listo", b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo \xe2\x80\x94 listo  ")
    elif action == "order":
        lines = data.split(b"\r\n")
        data = b"\r\n".join([lines[2], lines[1], lines[0], lines[3]])
    with open(path, "wb") as handle:
        handle.write(data)


def main():
    parent = tempfile.mkdtemp(prefix="m10-probe-", dir=BASE)
    try:
        outcomes = [run_case(parent, "reference")]
        for action in ("none", "double", "crlf", "leading", "spaces", "order"):
            outcomes.append(run_case(parent, action,
                                     lambda case, a=action: tweak(case, a)))
        outcomes.append(run_case(parent, "wrong",
                                 lambda case: tweak(case, "order"), reference_answer=False))
        outcomes.append(run_case(parent, "untouched", reference_answer=False))
        print("; ".join(outcomes))
    finally:
        shutil.rmtree(parent)


if __name__ == "__main__":
    main()
