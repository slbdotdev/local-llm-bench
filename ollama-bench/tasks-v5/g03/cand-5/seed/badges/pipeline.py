"""Stateful orchestration for badge batches."""

from . import core, formatting


class BadgePipeline:
    def __init__(self, tone="plain", builder=core.make_tag):
        self.tone = tone
        self.builder = builder
        self.items = []

    def add(self, label):
        self.items.append(label)
        return self

    def extend(self, labels):
        for label in labels:
            self.add(label)
        return self

    def values(self):
        return [self.builder(label, self.tone) for label in self.items]

    def render(self, separator="\n"):
        return separator.join(self.values())

    def summary(self):
        return {"count": len(self.items), "values": self.values(),
                "tone": self.tone}

    def reset(self):
        self.items[:] = []
        return self


def pipeline_for(labels, tone="plain"):
    return BadgePipeline(tone=tone).extend(labels)


def pipeline_text(labels, tone="plain"):
    return pipeline_for(labels, tone=tone).render()


def pipeline_table(groups, tone="plain"):
    return formatting.render_table(groups, tone=tone)
