"""Run the reference solution on a complete copied project."""
import importlib.util
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent


def _load(path):
    sys.path.insert(0, str(pathlib.Path(path).parent.parent))
    spec = importlib.util.spec_from_file_location("_selfcheck_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_tree(destination):
    for name in ("src", "data", "policies", "history", "README.md",
                 "check_project.py"):
        source = ROOT / "seed" / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def _run_checker(source_bytes=None, remove_target=False):
    with tempfile.TemporaryDirectory() as raw:
        work = pathlib.Path(raw)
        _copy_tree(work)
        shutil.copy2(ROOT / "test.py", work / "_hidden_test.py")
        target = work / "src" / "reconcile.py"
        if remove_target:
            target.unlink()
        elif source_bytes is not None:
            target.write_bytes(source_bytes)
        result = subprocess.run([sys.executable, "_hidden_test.py"], cwd=work,
                                text=True, capture_output=True, timeout=10)
        verdict = next((line for line in result.stdout.splitlines()
                         if line.startswith("VERDICT ")), "VERDICT missing")
        return result.returncode, verdict, result.stdout


def main():
    with tempfile.TemporaryDirectory() as raw:
        work = pathlib.Path(raw)
        _copy_tree(work)
        shutil.copy2(ROOT / "ref" / "reconcile.py", work / "src" / "reconcile.py")
        module = _load(work / "src" / "reconcile.py")
        report = module.reconcile()
        assert set(report) == {"total_usd", "by_account", "by_tax_code",
                               "accepted_ids", "accepted_count"}
        assert report["accepted_count"] == len(report["accepted_ids"])
        assert list(report["by_account"]) == sorted(report["by_account"])
        assert list(report["by_tax_code"]) == sorted(report["by_tax_code"])
        assert report["total_usd"] == sum(report["by_account"].values(),
                                          module.Decimal("0"))
        rendered = module.format_report(report)
        assert len(rendered.splitlines()) == 5
        print("reference report: ok")
        print("reference total:", report["total_usd"])
        print("accepted count:", report["accepted_count"])
        print("reference accounts:", repr(report["by_account"]))
        print("reference taxes:", repr(report["by_tax_code"]))
        print("reference ids:", repr(report["accepted_ids"]))
        print("reference ids hash:", hashlib.sha256(",".join(report["accepted_ids"]).encode()).hexdigest())
        print("reference rendering: ok")
        correct = (ROOT / "ref" / "reconcile.py").read_bytes()
        text = correct.decode()
        first = text.index("def _entries():")
        second = text.index("def _row_usd(row):")
        end = text.index("\n\ndef reconcile():", second)
        reordered = (text[:first] + text[second:end].rstrip("\n") +
                     "\n\n" + text[first:second].rstrip("\n") + text[end:])
        probes = [
            ("A7-1 no trailing newline", correct.rstrip(b"\n"), 0, "VERDICT correct"),
            ("A7-2 two trailing newlines", correct.rstrip(b"\n") + b"\n\n",
             0, "VERDICT correct"),
            ("A7-3 CRLF", correct.replace(b"\n", b"\r\n"), 0, "VERDICT correct"),
            ("A7-4 leading blank line", b"\n" + correct, 0, "VERDICT correct"),
            ("A7-5 trailing spaces", correct.replace(
                b'"""Reconciliation report for the 2025-12-31 ledger close."""\n',
                b'"""Reconciliation report for the 2025-12-31 ledger close."""  \n',
            ), 0, "VERDICT correct"),
            ("A7-6 reordered helpers", reordered.encode(), 0, "VERDICT correct"),
            ("wrong plausible", text.replace(
                'if row["state"] != "posted":',
                'if row["state"] not in ("posted", "captured"):',
            ).encode(), 1, "VERDICT confidently_wrong"),
        ]
        code, verdict, output = _run_checker(correct)
        print("test.py against ref: " + output.replace("\n", " | ").strip())
        assert code == 0 and verdict == "VERDICT correct"
        for label, source, expected_code, expected_verdict in probes:
            code, verdict, unused_output = _run_checker(source)
            okay = code == expected_code and verdict == expected_verdict
            print(label + ": " + ("ok" if okay else "BAD") +
                  " :: " + str(code) + " " + verdict)
            assert okay
        code, verdict, unused_output = _run_checker(remove_target=True)
        okay = code == 1 and verdict == "VERDICT visibly_failed"
        print("untouched sandbox: " + ("ok" if okay else "BAD") +
              " :: " + str(code) + " " + verdict)
        assert okay
    return 0


if __name__ == "__main__":
    sys.exit(main())
