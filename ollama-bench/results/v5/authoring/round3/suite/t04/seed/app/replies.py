from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    status: int
    body: dict
    headers: dict


def accepted(identity):
    return Response(200, {"authenticated": True, "identity": identity.key()}, {})


def denied():
    return Response(401, {"authenticated": False}, {})


def blocked():
    return Response(429, {"authenticated": False, "retryable": True},
                    {"Retry-After": "60"})


def bad_request(message):
    return Response(400, {"error": str(message)}, {})


def service_unavailable():
    return Response(503, {"error": "temporarily unavailable"}, {})


def is_authenticated(response):
    return response.status == 200 and response.body.get("authenticated") is True
