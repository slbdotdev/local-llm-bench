"""Route lookup helpers for a tiny web gateway."""

_default_routes = {}


def resolve(path, routes=None):
    if routes is None:
        routes = _default_routes
    if path is None:
        return "/404"
    key = path.strip()
    if key == "":
        return "/404"
    try:
        return routes.get(key, "/404")
    except Exception:
        return "/404"


def remember(path, destination, routes=None):
    if routes is None:
        routes = _default_routes
    routes[path.strip()] = destination
    return resolve(path, routes)
