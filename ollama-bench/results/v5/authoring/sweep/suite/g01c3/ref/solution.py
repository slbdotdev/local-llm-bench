"""Reference implementation for the seeded transformation."""


def _is_ascii_word(ch):
    return ("a" <= ch <= "z" or "A" <= ch <= "Z" or
            "0" <= ch <= "9" or ch == "_")


def transform(text: str) -> str:
    out = []
    i = 0
    wrapped = 0
    n = len(text)
    while i < n:
        if text[i] == "#" and (i == 0 or text[i - 1] == " "):
            out.append(text[i:])
            break
        if "0" <= text[i] <= "9":
            start = i
            while i < n and "0" <= text[i] <= "9":
                i += 1
            run = text[start:i]
            left_ok = start == 0 or not _is_ascii_word(text[start - 1])
            right_ok = i == n or not _is_ascii_word(text[i])
            if left_ok and right_ok and wrapped < 3:
                out.extend(("<", run, ">"))
                wrapped += 1
            else:
                out.append(run)
            if wrapped == 3:
                out.append(text[i:])
                break
            continue
        out.append(text[i])
        i += 1
    return "".join(out)
