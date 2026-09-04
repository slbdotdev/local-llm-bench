"""Setup + grading for the Sonnet v4 difficulty probe.

  python results/sonnet-v4/run.py setup           # build sandboxes + manifest
  python results/sonnet-v4/run.py grade [keys...] # grade all / given keys

Grading is identical to results/haiku-v4/_grade.py (== pibench.run_pi):
hidden test.py copied in as _hidden_test.py, `python _hidden_test.py` with
cwd=sandbox, PYTHONUTF8=1 PYTHONIOENCODING=utf-8, 60 s timeout with
process-tree kill; pass iff rc==0 and "PASS" in stdout; score = parse_score.
"""
import os, sys, json, time, shutil

BASE = r"C:\Users\slb\ollama-bench"
sys.path.insert(0, BASE)
import pibench

ROOT = os.path.join(BASE, 'results', 'sonnet-v4')
TASKS = ['52_reengine', '55_minilang', '56_tmpl', '57_stateful', '59_uri', '60_numlit', '61_codecs']
TRIALS = 3
MANP = os.path.join(ROOT, 'manifest.json')
GRADEP = os.path.join(ROOT, 'grades.json')


def setup():
    man = {}
    for task in TASKS:
        tdir = os.path.join(BASE, 'tasks-v4', task)
        seed = os.path.join(tdir, 'seed')
        for k in range(1, TRIALS + 1):
            sb = os.path.join(ROOT, task, 't%d' % k)
            os.makedirs(sb, exist_ok=True)
            for name in os.listdir(seed):
                src = os.path.join(seed, name)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(sb, name), dirs_exist_ok=True)
                else:
                    shutil.copy(src, os.path.join(sb, name))
            shutil.copy(os.path.join(tdir, 'prompt.md'), os.path.join(sb, 'TASK.md'))
            man['%s/t%d' % (task, k)] = {
                'sandbox': sb,
                'test': os.path.join(tdir, 'test.py'),
                'task': task,
                'trial': k,
                'tasks_dir': 'tasks-v4',
            }
    json.dump(man, open(MANP, 'w'), indent=1)
    print('setup: %d sandboxes' % len(man))


def grade(keys):
    man = json.load(open(MANP))
    grades = json.load(open(GRADEP)) if os.path.exists(GRADEP) else {}
    keys = keys or list(man)
    for key in keys:
        e = man[key]
        sb = e['sandbox']
        shutil.copy(e['test'], os.path.join(sb, '_hidden_test.py'))
        t0 = time.time()
        so, se, rc, to = pibench.run_tree([sys.executable, '_hidden_test.py'], 60, cwd=sb,
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            encoding="utf-8", errors="replace")
        wall = round(time.time() - t0, 1)
        if to:
            tail, passed, score = "grader timeout", False, 0.0
        else:
            tail = (so + se)[-300:].strip()
            passed = rc == 0 and "PASS" in so
            score = pibench.parse_score(so)
        grades[key] = {'task': e['task'], 'trial': e['trial'], 'pass': passed,
                       'score': score, 'grader': tail, 'wall_s': wall}
        print(key, 'PASS' if passed else 'FAIL', 'score=', score, wall)
    json.dump(grades, open(GRADEP, 'w'), indent=1)


def mark_timeout(keys):
    """Record a taker that blew its wall-clock limit: fail, score 0."""
    man = json.load(open(MANP))
    grades = json.load(open(GRADEP)) if os.path.exists(GRADEP) else {}
    for key in keys:
        e = man[key]
        grades[key] = {'task': e['task'], 'trial': e['trial'], 'pass': False,
                       'score': 0.0, 'grader': 'taker timeout (25 min)', 'wall_s': 0.0}
        print(key, 'taker timeout')
    json.dump(grades, open(GRADEP, 'w'), indent=1)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'grade'
    if cmd == 'setup':
        setup()
    elif cmd == 'timeout':
        mark_timeout(sys.argv[2:])
    else:
        grade(sys.argv[2:])
