"""Set OLLAMA_KV_CACHE_TYPE and restart Ollama so the server picks it up.

The variable is read by the server process at start, so setx alone does nothing;
the app must be restarted. Written as a file rather than inlined because it crosses
WSL -> Windows and every extra quoting layer is a place for it to run somewhere else.

Usage: kv_cache_switch.py <q4_0|q8_0>
"""
import os, subprocess, sys, time, urllib.request

VALUE = sys.argv[1]
assert VALUE in ("q4_0", "q8_0"), VALUE
EXE = os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama app.exe")

subprocess.run(["setx", "OLLAMA_KV_CACHE_TYPE", VALUE], capture_output=True, text=True)
for image in ("ollama app.exe", "ollama.exe"):
    subprocess.run(["taskkill", "/IM", image, "/F"], capture_output=True, text=True)
time.sleep(3)

env = dict(os.environ)
env["OLLAMA_KV_CACHE_TYPE"] = VALUE
subprocess.Popen([EXE], env=env, close_fds=True)

deadline = time.time() + 90
ok = False
while time.time() < deadline:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            if r.status == 200:
                ok = True
                break
    except Exception:
        time.sleep(2)
print(f"OLLAMA_KV_CACHE_TYPE={VALUE} api_up={ok}")
