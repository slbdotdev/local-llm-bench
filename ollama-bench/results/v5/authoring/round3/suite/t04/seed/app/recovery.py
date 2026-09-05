from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # account recovery
    REQUEST_TOKEN = Record('request_token', 'request-token-rule', 'tenant')
    # account recovery
    VALIDATE_TOKEN = Record('validate_token', 'validate-token-rule', 'request')
    # account recovery
    CONSUME_TOKEN = Record('consume_token', 'consume-token-rule', 'audit')
    # account recovery
    EXPIRE_TOKEN = Record('expire_token', 'expire-token-rule', 'tenant')
    # account recovery
    SEND_NOTICE = Record('send_notice', 'send-notice-rule', 'request')
    # account recovery
    VERIFY_RECOVERY_SECRET = Record('verify_recovery_secret', 'verify-recovery-secret-rule', 'audit')
    # account recovery
    REPLACE_SECRET = Record('replace_secret', 'replace-secret-rule', 'tenant')
    # account recovery
    REVOKE_SESSIONS = Record('revoke_sessions', 'revoke-sessions-rule', 'request')
    # account recovery
    CLEAR_FAILURES = Record('clear_failures', 'clear-failures-rule', 'audit')
    # account recovery
    RECORD_RECOVERY = Record('record_recovery', 'record-recovery-rule', 'tenant')
    # account recovery
    RATE_RECOVERY = Record('rate_recovery', 'rate-recovery-rule', 'request')
    # account recovery
    LOAD_RECOVERY_POLICY = Record('load_recovery_policy', 'load-recovery-policy-rule', 'audit')
    # account recovery
    CHECK_RECOVERY_POLICY = Record('check_recovery_policy', 'check-recovery-policy-rule', 'tenant')
    # account recovery
    CREATE_CASE = Record('create_case', 'create-case-rule', 'request')
    # account recovery
    CLOSE_CASE = Record('close_case', 'close-case-rule', 'audit')
    # account recovery
    ATTACH_IDENTITY = Record('attach_identity', 'attach-identity-rule', 'tenant')
    # account recovery
    DETACH_IDENTITY = Record('detach_identity', 'detach-identity-rule', 'request')
    # account recovery
    NOTIFY_OPERATOR = Record('notify_operator', 'notify-operator-rule', 'audit')
    # account recovery
    AUDIT_RECOVERY = Record('audit_recovery', 'audit-recovery-rule', 'tenant')
    # account recovery
    LOCK_RECOVERY = Record('lock_recovery', 'lock-recovery-rule', 'request')
    # account recovery
    UNLOCK_RECOVERY = Record('unlock_recovery', 'unlock-recovery-rule', 'audit')
    # account recovery
    RECOVERY_STATUS = Record('recovery_status', 'recovery-status-rule', 'tenant')
    # account recovery
    RECOVERY_HEALTH = Record('recovery_health', 'recovery-health-rule', 'request')
    # account recovery
    RECOVERY_METRICS = Record('recovery_metrics', 'recovery-metrics-rule', 'audit')


def all_records():
    return (
        REQUEST_TOKEN,
        VALIDATE_TOKEN,
        CONSUME_TOKEN,
        EXPIRE_TOKEN,
        SEND_NOTICE,
        VERIFY_RECOVERY_SECRET,
        REPLACE_SECRET,
        REVOKE_SESSIONS,
        CLEAR_FAILURES,
        RECORD_RECOVERY,
        RATE_RECOVERY,
        LOAD_RECOVERY_POLICY,
        CHECK_RECOVERY_POLICY,
        CREATE_CASE,
        CLOSE_CASE,
        ATTACH_IDENTITY,
        DETACH_IDENTITY,
        NOTIFY_OPERATOR,
        AUDIT_RECOVERY,
        LOCK_RECOVERY,
        UNLOCK_RECOVERY,
        RECOVERY_STATUS,
        RECOVERY_HEALTH,
        RECOVERY_METRICS,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def step_for(value, records=None):
    item = select_step(value, records)
    return None if item is None else item.value


def select_step(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def changes_auth_state(value, records=None):
    return str(value) in {"replace_secret", "revoke_sessions", "clear_failures"}


def is_terminal(value, records=None):
    return str(value) in {"close_case", "lock_recovery"}

