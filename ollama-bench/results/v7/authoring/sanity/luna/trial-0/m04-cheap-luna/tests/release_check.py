"""Small release gate for the dispatch completion state."""

from ember.dispatch_store import DISPATCH_STATES, DispatchGateway


def main():
    engine = DispatchGateway()
    record = engine.expand("release-check")
    assert record["state"] == "expanded"
    assert engine.snapshot()[0]["state"] == "expanded"


if __name__ == "__main__":
    main()
