"""Generic grader self-test: for every task dir under the given tasks directory,
the reference solution in <task>/ref/ must PASS the hidden test.py, and (for seeded
tasks) the untouched seed must FAIL it.  Usage: python selftest2.py [tasks-v2] [task ...]"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def run_grader(sb, test):
    shutil.copy(test, os.path.join(sb, "_hidden_test.py"))
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180, env=env)
    return r.returncode == 0 and "PASS" in r.stdout, (r.stdout + r.stderr).strip()[-400:]


def main():
    args = sys.argv[1:]
    tdir = os.path.join(HERE, args[0] if args else "tasks-v2")
    only = set(args[1:])
    bad = 0
    for name in sorted(os.listdir(tdir)):
        d = os.path.join(tdir, name)
        if not os.path.isdir(d) or (only and name not in only):
            continue
        test, seed, ref = os.path.join(d, "test.py"), os.path.join(d, "seed"), os.path.join(d, "ref")
        problems = []
        if not os.path.exists(os.path.join(d, "prompt.md")): problems.append("no prompt.md")
        if not os.path.exists(test): problems.append("no test.py")
        if not os.path.isdir(ref): problems.append("no ref/ solution")
        if problems:
            print(f"{name:18s} INVALID {problems}"); bad += 1; continue
        sb = tempfile.mkdtemp(prefix="st2_")
        if os.path.isdir(seed): shutil.copytree(seed, sb, dirs_exist_ok=True)
        shutil.copytree(ref, sb, dirs_exist_ok=True)
        ok, out = run_grader(sb, test)
        print(f"{name:18s} ref  {'PASS' if ok else 'FAIL  ' + out[-300:]}")
        bad += not ok
        shutil.rmtree(sb, ignore_errors=True)
        if os.path.isdir(seed):
            sb2 = tempfile.mkdtemp(prefix="st2_"); shutil.copytree(seed, sb2, dirs_exist_ok=True)
            ok2, _ = run_grader(sb2, test)
            print(f"{name:18s} seed {'FAIL (good)' if not ok2 else 'PASS (BAD: seed must not pass)'}")
            bad += ok2
            shutil.rmtree(sb2, ignore_errors=True)
    print("selftest2", "OK" if not bad else f"{bad} problems")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
