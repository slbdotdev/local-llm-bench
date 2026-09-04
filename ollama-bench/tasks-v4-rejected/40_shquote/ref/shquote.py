"""POSIX-sh-like word splitting with quote removal, and minimal shell quoting."""

WHITESPACE = " \t\n\r"
SAFE = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "@%+=:,./_-"
)


class SplitError(ValueError):
    """Raised by split/quote/join.  .kind is one of type/escape/quote."""

    def __init__(self, kind, message=None):
        ValueError.__init__(self, message if message is not None else kind)
        self.kind = kind


def split(s):
    """Split a command line into words, removing quotes and escapes."""
    if not isinstance(s, str):
        raise SplitError("type", "split() argument must be a str")

    words = []
    buf = []
    started = False          # is a word in progress?
    i = 0
    n = len(s)

    while i < n:
        c = s[i]

        if c in WHITESPACE:
            if started:
                words.append("".join(buf))
                buf = []
                started = False
            i += 1

        elif c == "\\":
            if i + 1 >= n:
                raise SplitError("escape", "no character after backslash")
            buf.append(s[i + 1])
            started = True
            i += 2

        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise SplitError("quote", "unterminated single quote")
            buf.append(s[i + 1:j])
            started = True
            i = j + 1

        elif c == '"':
            i += 1
            started = True
            closed = False
            while i < n:
                d = s[i]
                if d == "\\":
                    if i + 1 >= n:
                        raise SplitError("escape", "no character after backslash")
                    e = s[i + 1]
                    if e == '"' or e == "\\":
                        buf.append(e)
                    else:
                        buf.append("\\")
                        buf.append(e)
                    i += 2
                elif d == '"':
                    i += 1
                    closed = True
                    break
                else:
                    buf.append(d)
                    i += 1
            if not closed:
                raise SplitError("quote", "unterminated double quote")

        else:
            buf.append(c)
            started = True
            i += 1

    if started:
        words.append("".join(buf))
    return words


def quote(word):
    """Return `word` quoted so that split(quote(word)) == [word]."""
    if not isinstance(word, str):
        raise SplitError("type", "quote() argument must be a str")
    if not word:
        return "''"
    for ch in word:
        if ch not in SAFE:
            break
    else:
        return word
    return "'" + word.replace("'", "'\"'\"'") + "'"


def join(words):
    """Quote every word and join them with single spaces."""
    if not isinstance(words, (list, tuple)):
        raise SplitError("type", "join() argument must be a list or tuple")
    return " ".join(quote(w) for w in words)
