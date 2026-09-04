"""A from-scratch CSV writer/reader with a configurable dialect."""


class CsvError(ValueError):
    pass


_QUOTINGS = ("minimal", "all", "nonnumeric", "none")


def write_row(fields, delimiter=",", quotechar='"', escapechar=None,
              doublequote=True, quoting="minimal", lineterminator="\r\n",
              skipinitialspace=False):
    if quoting not in _QUOTINGS:
        raise CsvError("bad quoting value %r" % (quoting,))
    fields = list(fields)
    n = len(fields)
    out = []
    for i, f in enumerate(fields):
        if i:
            out.append(delimiter)
        if f is None:
            s = ""
        elif isinstance(f, str):
            s = f
        else:
            s = str(f)
        if quoting == "all":
            quoted = True
        elif quoting == "nonnumeric":
            quoted = not isinstance(f, (int, float))
        else:
            quoted = False
        buf = []
        for c in s:
            want_escape = False
            special = (c == delimiter or c == quotechar or c == "\r"
                       or c == "\n" or c in lineterminator
                       or (escapechar is not None and c == escapechar))
            if special:
                if quoting == "none":
                    want_escape = True
                else:
                    if c == quotechar:
                        if doublequote:
                            buf.append(quotechar)
                        else:
                            want_escape = True
                    elif escapechar is not None and c == escapechar:
                        want_escape = True
                    if not want_escape:
                        quoted = True
                if want_escape:
                    if escapechar is None:
                        raise CsvError("need to escape, but no escapechar set")
                    buf.append(escapechar)
            buf.append(c)
        if n == 1 and s == "":
            if quoting == "none":
                raise CsvError("single empty field record must be quoted")
            quoted = True
        if quoted:
            out.append(quotechar)
            out.append("".join(buf))
            out.append(quotechar)
        else:
            out.append("".join(buf))
    out.append(lineterminator)
    return "".join(out)


def _split_lines(text):
    lines = []
    start = 0
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\n":
            lines.append(text[start:i + 1])
            i += 1
            start = i
        elif c == "\r":
            if i + 1 < n and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
            lines.append(text[start:i])
            start = i
        else:
            i += 1
    if start < n:
        lines.append(text[start:])
    return lines


def read_rows(text, delimiter=",", quotechar='"', escapechar=None,
              doublequote=True, quoting="minimal", lineterminator="\r\n",
              skipinitialspace=False):
    if quoting not in _QUOTINGS:
        raise CsvError("bad quoting value %r" % (quoting,))
    rows = []
    fields = []
    buf = []
    numeric = [False]
    state = ["START_RECORD"]

    def save_field():
        s = "".join(buf)
        del buf[:]
        if quoting == "nonnumeric" and numeric[0]:
            try:
                s = float(s)
            except ValueError:
                raise CsvError("could not convert %r to float" % (s,))
        numeric[0] = False
        fields.append(s)

    EOL = None

    def step(c):
        st = state[0]
        if st == "START_RECORD":
            if c is EOL:
                return
            if c == "\n" or c == "\r":
                state[0] = "EAT_CRNL"
                return
            state[0] = "START_FIELD"
            st = "START_FIELD"
        if st == "START_FIELD":
            if c is EOL or c == "\n" or c == "\r":
                save_field()
                state[0] = "START_RECORD" if c is EOL else "EAT_CRNL"
            elif c == quotechar and quoting != "none":
                state[0] = "IN_QUOTED_FIELD"
            elif escapechar is not None and c == escapechar:
                if quoting == "nonnumeric":
                    numeric[0] = True
                state[0] = "ESCAPED_CHAR"
            elif c == " " and skipinitialspace:
                pass
            elif c == delimiter:
                save_field()
            else:
                if quoting == "nonnumeric":
                    numeric[0] = True
                buf.append(c)
                state[0] = "IN_FIELD"
            return
        if st == "ESCAPED_CHAR":
            if c == "\n" or c == "\r":
                buf.append(c)
                state[0] = "AFTER_ESCAPED_CRNL"
                return
            buf.append("\n" if c is EOL else c)
            state[0] = "IN_FIELD"
            return
        if st == "AFTER_ESCAPED_CRNL":
            if c is EOL:
                return
            st = "IN_FIELD"
            state[0] = "IN_FIELD"
        if st == "IN_FIELD":
            if c is EOL or c == "\n" or c == "\r":
                save_field()
                state[0] = "START_RECORD" if c is EOL else "EAT_CRNL"
            elif escapechar is not None and c == escapechar:
                state[0] = "ESCAPED_CHAR"
            elif c == delimiter:
                save_field()
                state[0] = "START_FIELD"
            else:
                buf.append(c)
            return
        if st == "IN_QUOTED_FIELD":
            if c is EOL:
                return
            if escapechar is not None and c == escapechar:
                state[0] = "ESCAPE_IN_QUOTED_FIELD"
            elif c == quotechar and quoting != "none":
                state[0] = "QUOTE_IN_QUOTED_FIELD" if doublequote else "IN_FIELD"
            else:
                buf.append(c)
            return
        if st == "ESCAPE_IN_QUOTED_FIELD":
            buf.append("\n" if c is EOL else c)
            state[0] = "IN_QUOTED_FIELD"
            return
        if st == "QUOTE_IN_QUOTED_FIELD":
            if quoting != "none" and c == quotechar:
                buf.append(quotechar)
                state[0] = "IN_QUOTED_FIELD"
            elif c == delimiter:
                save_field()
                state[0] = "START_FIELD"
            elif c is EOL or c == "\n" or c == "\r":
                save_field()
                state[0] = "START_RECORD" if c is EOL else "EAT_CRNL"
            else:
                buf.append(c)
                state[0] = "IN_FIELD"
            return
        if st == "EAT_CRNL":
            if c == "\n" or c == "\r":
                return
            if c is EOL:
                state[0] = "START_RECORD"
                return
            raise CsvError("new-line character seen in unquoted field")

    for line in _split_lines(text):
        for ch in line:
            step(ch)
        step(EOL)
        if state[0] == "START_RECORD":
            rows.append(fields[:])
            del fields[:]
    if buf or state[0] == "IN_QUOTED_FIELD":
        save_field()
        rows.append(fields[:])
        del fields[:]
    return rows
