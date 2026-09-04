"""Build clean sandboxes for a subscription-model gate trial, and grade them afterwards.

Sonnet and Haiku are subscription models, so they are gated as Claude Code subagents rather
than through pibench.py (which drives pi against ollama or OpenRouter). This script makes the
two halves of that identical to what pibench does, so the gate numbers mean the same thing:

  prep   sandbox <- seed/ only. Never ref/, never test.py, never NOTES.md.
  grade  test.py -> _hidden_test.py, run with cwd=sandbox, PYTHONUTF8=1, 60 s timeout;
         pass iff rc == 0 and "PASS" in stdout; SCORE and VERDICT parsed out.

Usage (WINDOWS python):
  python prep_gate_sandboxes.py prep  <gate-dir> <trial>
  python prep_gate_sandboxes.py grade <gate-dir> <trial>
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.join(HERE, "gate-suite")
SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)


def tasks():
    return sorted(t for t in os.listdir(SUITE) if os.path.isdir(os.path.join(SUITE, t)))


def prep(gate, trial):
    for t in tasks():
        sb = os.path.join(gate, f"trial-{trial}", t)
        if os.path.exists(sb):
            shutil.rmtree(sb)
        os.makedirs(sb)
        seed = os.path.join(SUITE, t, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sb, dirs_exist_ok=True)
        print(f"{t}: {sb}")
    print("\nprompts are at <suite>/<task>/prompt.md; never copy ref/ or test.py in")


def grade(gate, trial):
    out = {}
    for t in tasks():
        sb = os.path.join(gate, f"trial-{trial}", t)
        if not os.path.isdir(sb):
            out[t] = {"error": "no sandbox"}
            continue
        shutil.copy(os.path.join(SUITE, t, "test.py"),
                    os.path.join(sb, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            so, rc = p.stdout, p.returncode
        except subprocess.TimeoutExpired:
            so, rc = "", -1
        sc = SCORE_RE.findall(so)
        vd = VERDICT_RE.findall(so)
        os.remove(os.path.join(sb, "_hidden_test.py"))
        out[t] = {"pass": rc == 0 and "PASS" in so,
                  "score": f"{sc[-1][0]}/{sc[-1][1]}" if sc else None,
                  "verdict": vd[-1] if vd else None, "rc": rc,
                  "tail": so.strip()[-160:]}
        r = out[t]
        print(f"{t:5s} {'PASS' if r['pass'] else 'FAIL':4s} score={r['score']} "
              f"verdict={r['verdict']}")
    p = os.path.join(gate, f"trial-{trial}", "results.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    n = sum(1 for v in out.values() if v.get("pass"))
    print(f"\n{n}/{len(out)} passed -> {p}")


if __name__ == "__main__":
    mode, gate, trial = sys.argv[1], sys.argv[2], sys.argv[3]
    (prep if mode == "prep" else grade)(os.path.abspath(gate), trial)
