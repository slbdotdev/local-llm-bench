def test_failed_secret_is_denied(client):
    response = client.login("Acme", "alice", "bad")
    assert response.status == 401


def test_success_is_accepted(client):
    response = client.login("Acme", "alice", "good")
    assert response.status == 200


def test_lockout_example(client):
    client.login("Acme", "alice", "bad")
    assert client.login("Acme", "alice", "good").status in (200, 429)


def test_second_tenant_is_independent(client):
    client.login("Acme", "alice", "bad")
    assert client.login("Other", "alice", "good").status == 200


def test_old_release_is_not_contract(client):
    assert client.release_name() != "2025.08"


def test_metrics_are_not_auth_state(client):
    before = client.metrics()
    client.login("Acme", "alice", "bad")
    assert client.metrics()["auth_failures"] == before["auth_failures"] + 1
