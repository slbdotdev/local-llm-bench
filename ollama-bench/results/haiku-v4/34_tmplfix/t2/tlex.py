"""Tokenizer for the tiny template language."""

# All whitespace characters that str.strip() removes
BLANK = " \t\n\r\f\v"


class TemplateError(ValueError):
    """Raised for every template problem.  ``kind`` says which kind."""

    def __init__(self, kind, message=""):
        ValueError.__init__(self, "%s: %s" % (kind, message) if message else kind)
        self.kind = kind


def _find_closing_delimiter(text, start, close_delim):
    """Find the closing delimiter, respecting string boundaries.

    Returns (end_pos, has_dash) where end_pos is the position of the closing
    delimiter (or -1 if not found), and has_dash is True if there's a dash
    right before the closing delimiter.

    Raises TemplateError if a string literal is unclosed.
    """
    i = start
    while i < len(text):
        if text[i] == "'":
            # Start of string literal - find the closing quote
            j = text.find("'", i + 1)
            if j < 0:
                raise TemplateError("syntax", "unterminated string literal")
            i = j + 1
        elif text[i:i+len(close_delim)] == close_delim:
            # Check for dash before closing delimiter
            has_dash = i > 0 and text[i - 1] == "-"
            return (i, has_dash)
        else:
            i += 1
    return (-1, False)


def tokenize(text):
    """Turn template text into a flat list of tokens.

    Tokens are ("text", s), ("var", expr_source) or ("tag", tag_source).
    Whitespace control markers are consumed here and are not part of the
    returned sources.
    """
    toks = []
    i = 0
    pending_lstrip = False
    while True:
        a = text.find("{{", i)
        b = text.find("{%", i)
        if a < 0:
            j = b
        elif b < 0:
            j = a
        else:
            j = a if a < b else b
        if j < 0:
            lit = text[i:]
            if pending_lstrip:
                lit = lit.lstrip(BLANK)
            if lit:
                toks.append(("text", lit))
            return toks
        kind = "var" if text[j:j + 2] == "{{" else "tag"
        close = "}}" if kind == "var" else "%}"
        k = j + 2
        strip_left = text.startswith("-", k)
        if strip_left:
            k += 1
        end, has_dash = _find_closing_delimiter(text, k, close)
        if end < 0:
            raise TemplateError("syntax", "unclosed tag")
        body = text[k:end]
        strip_right = has_dash
        if strip_right:
            body = body[:-1]
        lit = text[i:j]
        if pending_lstrip:
            lit = lit.lstrip(BLANK)
        if strip_left:
            lit = lit.rstrip(BLANK)
        if lit:
            toks.append(("text", lit))
        toks.append((kind, body))
        pending_lstrip = strip_right
        i = end + len(close)
