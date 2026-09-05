import os


INITIAL = {
    os.path.join("config", "formatting.ini"): b"# Configuraci\xc3\xb3n del cat\xc3\xa1logo\r\nwelcome=Ol\xc3\xa1, cat\xc3\xa1logo\r\nmode=leg\xc3\xadvel\r\n",
    os.path.join("docs", "operator_notes.txt"): b"owner=Zo\xc3\xab\r\nnote=Revisi\xc3\xb3n pendiente\r\nestado=vigente\r\n",
}
EXPECTED = {
    os.path.join("config", "formatting.ini"): [b"# Configuraci\xc3\xb3n del cat\xc3\xa1logo", b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo \xe2\x80\x94 listo", b"mode=leg\xc3\xadvel"],
    os.path.join("docs", "operator_notes.txt"): [b"owner=Zo\xc3\xab", b"note=Revisi\xc3\xb3n completa", b"estado=vigente"],
}


def finish(score, verdict):
    print("SCORE %d/1" % score)
    if score == 1 and verdict == "correct":
        print("PASS")
    print("VERDICT %s" % verdict)
    raise SystemExit(0 if score == 1 and verdict == "correct" else 1)


def normalized(data):
    if b"\r\n" not in data or b"\n" in data.replace(b"\r\n", b""):
        return None
    lines = data.split(b"\r\n")
    while lines and lines[0].strip(b" \t") == b"":
        lines.pop(0)
    while lines and lines[-1].strip(b" \t") == b"":
        lines.pop()
    return [line.rstrip(b" \t") for line in lines]


def main():
    root = os.getcwd()
    changed = False
    all_right = True
    for relative, expected in EXPECTED.items():
        path = os.path.join(root, relative)
        with open(path, "rb") as handle:
            data = handle.read()
        changed = changed or data != INITIAL[relative]
        all_right = all_right and normalized(data) is not None and set(normalized(data)) == set(expected)
    if all_right:
        finish(1, "correct")
    finish(0, "confidently_wrong" if changed else "visibly_failed")


try:
    main()
except SystemExit:
    raise
except Exception:
    finish(0, "visibly_failed")
