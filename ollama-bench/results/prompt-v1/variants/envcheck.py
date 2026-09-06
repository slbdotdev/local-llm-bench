import os
for k in ("ZAI_API_KEY", "PIBENCH_PI_ARGS", "OPENROUTER_API_KEY"):
    v = os.environ.get(k)
    print(k, "len=%d" % len(v) if v is not None else "ABSENT")
