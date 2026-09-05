"""Form field presenters."""

from .. import core, validation


def field(name, value, tone="plain", required=False):
    return {"name": name, "value": value, "required": required,
            "badge": core.make_tag(value, tone)}


def fields(values, tone="plain"):
    return [field(name, value, tone=tone) for name, value in values.items()]


def errors(values):
    return [name for name, value in values.items() if not validation.valid_label(value)]


def form(values, tone="plain"):
    return {"fields": fields(values, tone=tone), "errors": errors(values),
            "valid": not errors(values)}


def submit(values, tone="plain"):
    result = form(values, tone=tone)
    if not result["valid"]:
        raise ValueError(result["errors"])
    return result
