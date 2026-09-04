import sys, subprocess, os
fails = []
def check(name, cond):
    if not cond: fails.append(name)
def run(*args):
    return subprocess.run([sys.executable, "wc.py", *args], capture_output=True, text=True, encoding="utf-8", timeout=30, env={**os.environ, "PYTHONUTF8": "1"})
try:
    text = "The cat sat.\nthe Dog, the CAT!\n\n\"quoted\" word (cat) naïve naïve\nend"
    with open("_in.txt", "w", encoding="utf-8", newline="") as f:
        f.write(text)
    r = run("_in.txt")
    check("counts", r.returncode == 0 and r.stdout.split() == ["4", "13", str(len(text))])
    r = run("--top", "3", "_in.txt")
    check("top3", r.returncode == 0 and r.stdout.strip().splitlines() == ["cat 3", "the 3", "naïve 2"])
    r = run("--top", "50", "_in.txt")
    lines = r.stdout.strip().splitlines()
    check("top all", r.returncode == 0 and len(lines) == 8 and lines[:3] == ["cat 3", "the 3", "naïve 2"] and lines[-1] == "word 1")
    check("top order tail", lines[3:] == ["dog 1", "end 1", "quoted 1", "sat 1", "word 1"])
    with open("_empty.txt", "w", encoding="utf-8") as f:
        pass
    r = run("_empty.txt")
    check("empty", r.returncode == 0 and r.stdout.split() == ["0", "0", "0"])
    r = run("_nope_.txt")
    check("missing file", r.returncode == 2 and "error: no such file" in r.stderr)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    try:
        d = run("_in.txt"); t = run("--top", "3", "_in.txt")
        print("DIAG counts:", repr(d.stdout[-200:]), repr(d.stderr[-300:]), "| top3:", repr(t.stdout[-200:]), repr(t.stderr[-300:]))
    except Exception as e:
        print("DIAG error", repr(e))
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
