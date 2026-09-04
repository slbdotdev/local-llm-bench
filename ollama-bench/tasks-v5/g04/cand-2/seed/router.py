"""Route lookup helpers for a tiny web gateway."""

def resolve(path, routes={}):
    if path is None:
        return "/404"
    key = path.strip()
    if key is "":
        return "/404"
    try:
        return routes.get(key, "/404")
    except:
        return "/404"

def remember(path, destination, routes={}):
    routes[path.strip()] = destination
    return resolve(path, routes)
