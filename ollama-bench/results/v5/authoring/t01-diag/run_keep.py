"""Run pibench with PIBENCH_KEEP set from inside the Windows process.

WSL-side `VAR=x windows.exe` does not propagate VAR unless it is listed in WSLENV,
which is why setting it in the shell silently did nothing.
"""
import os, sys, runpy
os.environ["PIBENCH_KEEP"] = r"D:\local-llm-bench\ollama-bench\results\v5\authoring\t01-diag\keep"
sys.argv = ["pibench.py", "--provider", "openrouter", "--models", "z-ai/glm-5.3-flash",
            "--tasks-dir", r"results\v5\authoring\gate-suite", "--tasks", "t01",
            "--trials", "3", "--timeout", "600", "--think", "medium",
            "--tag", "gate-glm-t01diag2"]
runpy.run_path(r"D:\local-llm-bench\ollama-bench\pibench.py", run_name="__main__")
