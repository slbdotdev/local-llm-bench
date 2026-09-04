"""Reference implementation for the seeded lexical transformation."""


def _word(ch):
    return ("a" <= ch <= "z" or "A" <= ch <= "Z" or
            "0" <= ch <= "9" or ch == "_")


def _record(record):
    out = []
    quoted = False
    wrapped = 0
    i = 0
    n = len(record)
    while i < n:
        ch = record[i]
        if not quoted and ch == "#" and (i == 0 or record[i - 1] == " "):
            out.append(record[i:])
            break
        if ch == '"':
            backslashes = 0
            j = i - 1
            while j >= 0 and record[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                quoted = not quoted
            out.append(ch)
            i += 1
            continue
        if "0" <= ch <= "9":
            start = i
            while i < n and "0" <= record[i] <= "9":
                i += 1
            eligible = (not quoted and
                        (start == 0 or not _word(record[start - 1])) and
                        (i == n or not _word(record[i])))
            run = record[start:i]
            if eligible and wrapped < 2:
                out.extend(("<", run, ">"))
                wrapped += 1
                if wrapped == 2:
                    out.append(record[i:])
                    break
            else:
                out.append(run)
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def transform(text: str) -> str:
    return "\n".join(_record(record) for record in text.split("\n"))
