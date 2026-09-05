import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
TEST = ROOT / "test.py"
EXPECTED = "ANSWER: no\nEVIDENCE: 77: return any(result.applicable and result.passed for result in results)"
SOURCE = "return any(result.applicable and result.passed for result in results)"


def run_case(label, answer, expected_exit, expected_verdict, expected_pass):
    with tempfile.TemporaryDirectory(dir=ROOT) as name:
        work = pathlib.Path(name)
        shutil.copytree(ROOT / "seed", work / "seed")
        if answer is not None:
            (work / "answer.txt").write_text(answer, encoding="utf-8", newline="")
        result = subprocess.run(
            [sys.executable, str(TEST)], cwd=work, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10,
        )
        lines = result.stdout.splitlines()
        score = next((line for line in lines if line.startswith("SCORE ")), "")
        verdict = next((line for line in lines if line.startswith("VERDICT ")), "")
        has_pass = "PASS" in lines
        got = (result.returncode == expected_exit and verdict == expected_verdict and
               has_pass == expected_pass and len([x for x in lines if x.startswith("SCORE ")]) == 1 and
               len([x for x in lines if x.startswith("VERDICT ")]) == 1)
        print("%s: %s, %s" % (label, score, verdict))
        if not got:
            raise SystemExit("unexpected %s result: exit %d\n%s" %
                             (label, result.returncode, result.stdout))


def check_prompt():
    prompt = (ROOT / "prompt.md").read_text(encoding="utf-8")
    if "should_grant" not in prompt or "answer.txt" not in prompt:
        raise SystemExit("prompt is missing target or artifact instructions")
    if "decision.py" in prompt or "policy_chain.py" in prompt:
        raise SystemExit("prompt names a single source file")
    if prompt.count("ANSWER: <yes-or-no>") != 1 or prompt.count("EVIDENCE: <line-number>") != 1:
        raise SystemExit("prompt artifact template changed")
    words = prompt.split()
    if len(words) >= 2000:
        raise SystemExit("prompt is too long")
    print("prompt: target and fixed artifact order present; no single answer file named")


def check_oracle_source():
    path = ROOT / "seed" / "release_control" / "policy_chain.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[76].strip() != SOURCE:
        raise SystemExit("oracle evidence line does not match seed")
    if "return any(" not in lines[76]:
        raise SystemExit("expected live aggregation defect not present")
    print("oracle: expected evidence line matches current Python source")


def main():
    check_prompt()
    check_oracle_source()
    correct = EXPECTED + "\n"
    cases = [
        ("reference", correct, 0, "VERDICT correct", True),
        ("A7-1 no trailing newline", EXPECTED, 0, "VERDICT correct", True),
        ("A7-2 two trailing newlines", correct + "\n", 0, "VERDICT correct", True),
        ("A7-3 CRLF", correct.replace("\n", "\r\n"), 0, "VERDICT correct", True),
        ("A7-4 leading blank line", "\n" + correct, 0, "VERDICT correct", True),
        ("A7-5 trailing space", "ANSWER: no \nEVIDENCE: 77: " + SOURCE + "  \n", 0,
         "VERDICT correct", True),
        ("A7-6 order violation", "EVIDENCE: 77: " + SOURCE + "\nANSWER: no\n", 1,
         "VERDICT visibly_failed", False),
        ("plausible wrong positive", "ANSWER: yes\nEVIDENCE: 77: " + SOURCE + "\n", 1,
         "VERDICT confidently_wrong", False),
        ("untouched sandbox", None, 1, "VERDICT visibly_failed", False),
    ]
    for case in cases:
        run_case(*case)


if __name__ == "__main__":
    main()
