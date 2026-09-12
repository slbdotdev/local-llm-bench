import json
import sys

path = sys.argv[1]
reason = "VOID: wrong admitted material; roster requires cand-luna slot, not cand-glm"
with open(path, encoding="utf-8") as f:
    data = json.load(f)
count = 0
for model in data.values():
    for row in model.get("runs", []):
        if row.get("task") in {"m03-main-glm", "m09-main-glm"}:
            row["void"] = True
            row["acceptance_valid"] = False
            row["void_reason"] = reason
            count += 1
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1)
    f.write("\n")
print(count)
