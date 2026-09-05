import os


def apply(root):
    path = os.path.join(root, "src", "harbor", "schema_store.py")
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    old = "def build_schema(config):"
    method = "    def published_snapshot(self):\n        return [self._slots[k] for k in reversed(sorted(self._slots))]\n\n\n"
    assert old in text
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text.replace(old, method + old))

if __name__ == "__main__":
    apply(os.getcwd())
