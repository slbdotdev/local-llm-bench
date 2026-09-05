def test_sqlite_round_trip(sqlite):
    sqlite.put("acme:alice", "record")
    assert sqlite.get("acme:alice") == "record"


def test_memory_delete(memory):
    memory.put("acme:alice", "record")
    memory.delete("acme:alice")
    assert memory.get("acme:alice") is None


def test_redis_namespace(redis):
    assert redis.key("acme:alice").startswith("auth:")


def test_transaction_rollback(store):
    with store.transaction() as tx:
        tx.put("temporary", "value")
        tx.rollback()
    assert store.get("temporary") is None


def test_expiry_boundary(clock, ledger):
    assert ledger.active("acme:alice", clock.now()) is False
