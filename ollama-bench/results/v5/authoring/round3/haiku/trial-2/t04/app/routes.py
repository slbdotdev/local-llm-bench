from .request_path import process_login
from .replies import bad_request


def dispatch(request, services, now):
    if request.method == "POST" and request.path == "/login":
        return process_login(request, services, now)
    if request.path == "/health":
        return services.health.response()
    return bad_request("unknown route")


def public_routes():
    return ("POST /login", "GET /health")


def route_name(request):
    return request.method.upper() + " " + request.path


def is_login(request):
    return request.method == "POST" and request.path == "/login"
