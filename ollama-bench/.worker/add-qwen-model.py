import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
provider = data["providers"]["ollama"]
provider["baseUrl"] = "http://127.0.0.1:11435/v1"
models = provider.setdefault("models", [])
models[:] = [m for m in models if m.get("id") != "qwen3:8b"]
models.append({
    "id": "qwen3:8b",
    "name": "Qwen3 8B Q4_K_M",
    "reasoning": True,
    "contextWindow": 32768,
    "maxTokens": 32768,
    "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
})
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
