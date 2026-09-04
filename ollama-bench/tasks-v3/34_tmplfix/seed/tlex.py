"""Tokenizer for the tiny template language."""

BLANK = " \t"


class TemplateError(ValueError):
    """Raised for every template problem.  ``kind`` says which kind."""

    def __init__(self, kind, message=""):
        ValueError.__init__(self, "%s: %s" % (kind, message) if message else kind)
        self.kind = kind


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
        end = text.find(close, k)
        if end < 0:
            lit = text[i:]
            if pending_lstrip:
                lit = lit.lstrip(BLANK)
            if lit:
                toks.append(("text", lit))
            return toks
        body = text[k:end]
        strip_right = body.endswith("-")
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
        i = end + 2
