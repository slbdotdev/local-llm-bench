"""Read the Z.ai coding-plan quota. Prints numbers only; never the key.

Usage: python3 zai-quota.py [label]
Emits one terse line per window plus a raw JSON dump to results/prompt-v1/quota/.
"""
import json, os, sys, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("ZAI_API_KEY")
if not KEY:
    print("ZAI_API_KEY absent"); sys.exit(3)
URL = "https://api.z.ai/api/monitor/usage/quota/limit"
label = sys.argv[1] if len(sys.argv) > 1 else "read"

req = urllib.request.Request(URL, headers={"Authorization": "Bearer " + KEY,
                                           "Accept": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
except Exception as e:
    print("QUOTA-UNREADABLE %s: %s" % (type(e).__name__, str(e)[:150])); sys.exit(1)

data = json.loads(body)
now = datetime.datetime.now(datetime.timezone.utc)
os.makedirs(os.path.join(HERE, "quota"), exist_ok=True)
stamp = now.strftime("%Y%m%dT%H%M%SZ")
with open(os.path.join(HERE, "quota", "%s-%s.json" % (stamp, label)), "w") as f:
    json.dump(data, f, indent=1, sort_keys=True)

UNIT = {3: "hour", 6: "week", 4: "day", 5: "month"}
print("QUOTA %s level=%s at %s" % (label, data["data"].get("level"), now.isoformat(timespec="seconds")))
worst5h = worstwk = None
for lim in data["data"]["limits"]:
    unit = UNIT.get(lim["unit"], "unit%s" % lim["unit"])
    window = "%s%s" % (lim["number"], unit)
    used, cap = lim["currentValue"], lim["usage"]
    pct = 100.0 * used / cap if cap else 0.0
    rt = lim.get("nextResetTime")  # null on a window nothing has touched since its reset
    reset = datetime.datetime.fromtimestamp(rt / 1000, datetime.timezone.utc).isoformat(timespec="seconds") if rt else "n/a"
    print("  window=%-7s used=%-8s cap=%-8s pct=%.2f%% remaining=%-8s reset=%s"
          % (window, used, cap, pct, lim["remaining"], reset))
    if unit == "hour":
        worst5h = pct
    if unit == "week":
        worstwk = pct
print("GATE 5h=%.2f%% (stop >80) week=%.2f%% (stop >60)" % (worst5h or 0.0, worstwk or 0.0))
if (worst5h or 0) > 80 or (worstwk or 0) > 60:
    print("GATE BREACHED"); sys.exit(2)
print("GATE OK")
