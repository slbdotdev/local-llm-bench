"""Command handlers used by the tiny command-line front end."""

from . import catalog, core, pipeline


def command_build(label, tone="plain"):
    return core.make_badge(label, tone=tone)


def command_batch(labels, tone="plain"):
    return core.batch(labels, tone=tone)


def command_catalog(names, tone=None):
    return catalog.select(names, tone=tone)


def command_pipe(labels, tone="plain"):
    pipe = pipeline.BadgePipeline(tone=tone)
    for label in labels:
        pipe.add(label)
    return pipe.values()


def dispatch(name, payload, tone="plain"):
    handlers = {"build": command_build, "batch": command_batch,
                "pipe": command_pipe}
    return handlers[name](payload, tone)


def parse_args(args):
    if not args:
        return "build", "", "plain"
    command = args[0]
    label = args[1] if len(args) > 1 else ""
    tone = args[2] if len(args) > 2 else "plain"
    return command, label, tone
