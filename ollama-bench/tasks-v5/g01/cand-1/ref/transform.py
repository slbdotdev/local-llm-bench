"""Reference implementation for the seeded path-record transformation."""


def _record(record):
    if record == "":
        return ""
    absolute = record.startswith("/")
    trailing = record.endswith("/")
    parts = []
    for segment in record.split("/"):
        if segment == "" or segment == ".":
            continue
        if segment == "..":
            for index in range(len(parts) - 1, -1, -1):
                if parts[index] != "..":
                    del parts[index]
                    break
            else:
                if not absolute:
                    parts.append("..")
        else:
            parts.append(segment)
    if parts:
        result = ("/" if absolute else "") + "/".join(parts)
        if trailing:
            result += "/"
        return result
    return "/" if absolute else "."


def transform(text):
    """Transform LF-separated slash records according to the seed spec."""
    return "\n".join(_record(record) for record in text.split("\n"))
