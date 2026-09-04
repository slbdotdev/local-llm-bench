import os, sys, json, time, shutil
sys.path.insert(0, os.path.abspath('.'))
import pibench
ROOT=os.path.join(os.path.abspath('.'),'results','haiku-v4')
man=json.load(open(os.path.join(ROOT,'manifest.json')))
gpath=os.path.join(ROOT,'grades.json')
grades=json.load(open(gpath)) if os.path.exists(gpath) else {}
keys=sys.argv[1:]
for key in keys:
    e=man[key]; sb=e['sandbox']
    shutil.copy(e['test'], os.path.join(sb,'_hidden_test.py'))
    t0=time.time()
    so,se,rc,to = pibench.run_tree([sys.executable,'_hidden_test.py'], 60, cwd=sb,
        env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"), encoding="utf-8", errors="replace")
    wall=round(time.time()-t0,1)
    if to:
        tail, passed, score = "grader timeout", False, 0.0
    else:
        tail=(so+se)[-300:].strip(); passed = rc==0 and "PASS" in so
        score = pibench.parse_score(so)
    grades[key]={'task':e['task'],'trial':e['trial'],'pass':passed,'score':score,'grader':tail,'wall_s':wall}
    print(key, 'PASS' if passed else 'FAIL', 'score=',score, wall)
json.dump(grades, open(gpath,'w'), indent=1)
