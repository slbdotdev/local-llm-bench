import pathlib
import shutil
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
TEST = ROOT / "test.py"
EXPECTED = "no"
LINE = 19
SOURCE_LINE = "for index in range(start, stop + 1):"


def run_case(label, answer):
    with tempfile.TemporaryDirectory(dir=ROOT) as name:
        work = pathlib.Path(name)
        shutil.copytree(ROOT / "seed", work / "seed")
        if answer is not None:
            (work / "answer.txt").write_text(answer, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(TEST)], cwd=work, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10,
        )
        lines = result.stdout.splitlines()
        verdict = next((line for line in lines if line.startswith("VERDICT ")), "")
        score = next((line for line in lines if line.startswith("SCORE ")), "")
        expected_exit = 0 if label == "reference" else 1
        expected_verdict = {
            "reference": "VERDICT correct",
            "near-miss": "VERDICT confidently_wrong",
            "empty": "VERDICT visibly_failed",
        }[label]
        status = "PASS" if label == "reference" else "FAIL"
        has_status = ("PASS" in lines if status == "PASS" else
                      any(line.startswith("FAIL ") for line in lines))
        ok = (result.returncode == expected_exit and verdict == expected_verdict and
              has_status)
        print("%s: %s, %s" % (label, score, verdict))
        if not ok:
            raise SystemExit("unexpected %s result: exit %d\n%s" %
                             (label, result.returncode, result.stdout))


prompt = (ROOT / "prompt.md").read_text(encoding="utf-8")
if "bounded_indices" not in prompt or "answer.txt" not in prompt:
    raise SystemExit("prompt is missing the target or artifact instructions")
if "catalog.py" in prompt:
    raise SystemExit("prompt names the answer file")
source_files = list((ROOT / "seed").glob("*.py"))
if len(source_files) != 1 or source_files[0].read_text(encoding="utf-8").splitlines()[LINE - 1].strip() != SOURCE_LINE:
    raise SystemExit("oracle evidence line does not match the seed")
print("prompt: target and artifact format present; no worked examples")

reference = (ROOT / "ref" / "answer.txt").read_text(encoding="utf-8")
near_miss = "ANSWER: yes\nEVIDENCE: %d: %s\n" % (LINE, SOURCE_LINE)
run_case("reference", reference)
run_case("near-miss", near_miss)
run_case("empty", None)
