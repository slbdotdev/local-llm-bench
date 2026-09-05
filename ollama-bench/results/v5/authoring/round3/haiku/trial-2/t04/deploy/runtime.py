from app.server import create_server


def build_runtime(container):
    return create_server(container).start()


def production_settings(environ):
    return {"environment": environ.get("ENVIRONMENT", "production"),
            "worker_count": int(environ.get("WORKER_COUNT", "4")),
            "request_timeout": int(environ.get("REQUEST_TIMEOUT", "30"))}


def ready(server):
    return server.started


def shutdown(server):
    server.stop()


def runtime_name():
    return "auth-service"
