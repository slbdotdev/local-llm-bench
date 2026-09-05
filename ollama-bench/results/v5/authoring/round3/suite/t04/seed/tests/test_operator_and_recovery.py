def test_operator_can_clear_lockout(operator):
    assert operator.authorize("clear_lockout")


def test_recovery_revokes_sessions(recovery):
    assert recovery.changes_auth_state("revoke_sessions")


def test_disabled_account_cannot_verify(verifier):
    assert verifier.verify_disabled() is False


def test_audit_redacts_secret(audit):
    assert "secret" not in audit.redacted_fields()


def test_policy_is_tenant_scoped(policy):
    assert policy.scope == "tenant"
