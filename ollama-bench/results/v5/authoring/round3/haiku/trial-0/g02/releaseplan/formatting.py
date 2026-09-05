"""The deliberately boring, byte-stable plan format."""


def render(target, platform, release, names, catalog, lock):
    lines = ["release=" + release + " platform=" + platform,
             "target=" + target]
    for name in names:
        lines.append("- " + name + "@" + lock[name]["version"]
                     + " requires=" + ",".join(lock[name]["deps"]))
    return "\n".join(lines) + "\n"


def parse_lines(text):
    return text.splitlines()
