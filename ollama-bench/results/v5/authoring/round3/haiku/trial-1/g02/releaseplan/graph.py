"""Dependency closure and stable dependency-first ordering."""


def closure(target, lock, canonical):
    result = []
    seen = set()

    def visit(name):
        name = canonical(name)
        if name in seen:
            return
        seen.add(name)
        row = lock.get(name)
        if row is None:
            raise KeyError(name)
        for dep in row["deps"]:
            visit(dep)
        result.append(name)

    visit(target)
    return result


def order(target, lock, catalog, canonical, allowed):
    names = closure(target, lock, canonical)
    if any(not allowed(name) for name in names):
        return []
    # closure is already dependency-first; stable priority only breaks ties
    # between independent branches without moving a dependency after a user.
    positions = {name: index for index, name in enumerate(names)}
    return sorted(names, key=lambda name: (positions[name], catalog[name]["priority"], name))
