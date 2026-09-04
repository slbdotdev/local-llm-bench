"""Strict INI-style configuration parser/serializer."""


class ConfigError(ValueError):
    pass


_UNESCAPE = {"\\": "\\", '"': '"', "n": "\n", "t": "\t"}


def _unquote(v):
    if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
        body = v[1:-1]
        out = []
        i = 0
        while i < len(body):
            c = body[i]
            if c == "\\":
                if i + 1 >= len(body):
                    raise ConfigError("trailing backslash in quoted value")
                nxt = body[i + 1]
                if nxt not in _UNESCAPE:
                    raise ConfigError("bad escape")
                out.append(_UNESCAPE[nxt])
                i += 2
            elif c == '"':
                raise ConfigError("unescaped quote in quoted value")
            else:
                out.append(c)
                i += 1
        return "".join(out)
    return v


def parse(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    cfg = {}
    cur = None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line[0] in "#;":
            continue
        if line[0] == "[":
            if not line.endswith("]"):
                raise ConfigError("bad section header: %r" % raw)
            name = line[1:-1].strip()
            if not name or "[" in name or "]" in name:
                raise ConfigError("bad section name: %r" % raw)
            cur = name
            if name not in cfg:
                cfg[name] = {}
            continue
        if "=" not in line:
            raise ConfigError("expected 'key = value': %r" % raw)
        k, _, v = line.partition("=")
        k = k.strip()
        if not k:
            raise ConfigError("empty key: %r" % raw)
        if cur is None:
            raise ConfigError("key outside of any section: %r" % raw)
        if k in cfg[cur]:
            raise ConfigError("duplicate key %r in section %r" % (k, cur))
        cfg[cur][k] = _unquote(v.strip())
    return cfg


def _needs_quote(v):
    return v == "" or v != v.strip() or any(c in v for c in '"\\\n\t')


def _quote(v):
    out = ['"']
    for c in v:
        if c == "\\":
            out.append("\\\\")
        elif c == '"':
            out.append('\\"')
        elif c == "\n":
            out.append("\\n")
        elif c == "\t":
            out.append("\\t")
        else:
            out.append(c)
    out.append('"')
    return "".join(out)


def dumps(cfg):
    blocks = []
    for sec, items in cfg.items():
        lines = ["[%s]" % sec]
        for k, v in items.items():
            lines.append("%s = %s" % (k, _quote(v) if _needs_quote(v) else v))
        blocks.append("\n".join(lines))
    if not blocks:
        return ""
    return "\n\n".join(blocks) + "\n"
