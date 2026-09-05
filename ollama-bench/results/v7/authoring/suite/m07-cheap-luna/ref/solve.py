import os


def apply(root):
    for base, dirs, names in os.walk(root):
        dirs[:] = [item for item in dirs if item not in ("__pycache__", ".pytest_cache")]
        for name in names:
            if name.endswith((".pyc", ".pyo")):
                continue
            path = os.path.join(base, name)
            with open(path, "r", encoding="utf-8", newline="") as handle:
                text = handle.read()
            if "build_watermark" in text:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    handle.write(text.replace("build_watermark", "load_watermark"))

if __name__ == "__main__":
    apply(os.getcwd())
