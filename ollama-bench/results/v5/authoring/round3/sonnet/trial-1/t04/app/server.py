from .clock import Clock
from .routes import dispatch


class Server:
    def __init__(self, services, clock=None):
        self.services = services
        self.clock = clock or Clock()
        self.started = False

    def start(self):
        self.started = True
        return self

    def handle(self, request):
        if not self.started:
            raise RuntimeError("server is not started")
        return dispatch(request, self.services, self.clock.now())

    def stop(self):
        self.started = False


def create_server(container):
    return Server(container.services, container.clock)


def health_payload(server):
    return {"started": server.started}
