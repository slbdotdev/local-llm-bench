"""Registration lifecycle for extensions that provide badge builders."""

from . import core


class Registry:
    def __init__(self):
        self._builders = {"default": core.make_tag}

    def register(self, name, builder):
        if not callable(builder):
            raise TypeError(name)
        self._builders[name] = builder

    def unregister(self, name):
        return self._builders.pop(name, None)

    def resolve(self, name="default"):
        return self._builders[name]

    def build(self, name, label, tone="plain"):
        return self.resolve(name)(label, tone)

    def build_many(self, name, labels, tone="plain"):
        builder = self.resolve(name)
        return [builder(label, tone) for label in labels]

    def names(self):
        return tuple(self._builders)


def default_registry():
    return Registry()
