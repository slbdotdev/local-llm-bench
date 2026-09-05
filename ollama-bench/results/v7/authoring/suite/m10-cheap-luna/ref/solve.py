import os


def apply(root):
    changes = {
        os.path.join("config", "formatting.ini"): (b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo", b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo \xe2\x80\x94 listo"),
        os.path.join("docs", "operator_notes.txt"): (b"note=Revisi\xc3\xb3n pendiente", b"note=Revisi\xc3\xb3n completa"),
    }
    for relative, (old, new) in changes.items():
        path = os.path.join(root, relative)
        with open(path, "rb") as handle:
            data = handle.read()
        assert data.count(old) == 1
        with open(path, "wb") as handle:
            handle.write(data.replace(old, new))

if __name__ == "__main__":
    apply(os.getcwd())
