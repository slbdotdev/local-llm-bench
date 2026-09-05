from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # audit schema
    AUTH_FAILED = Record('auth_failed', 'auth-failed-rule', 'tenant')
    # audit schema
    AUTH_BLOCKED = Record('auth_blocked', 'auth-blocked-rule', 'request')
    # audit schema
    AUTH_SUCCEEDED = Record('auth_succeeded', 'auth-succeeded-rule', 'audit')
    # audit schema
    IDENTITY_NORMALIZED = Record('identity_normalized', 'identity-normalized-rule', 'tenant')
    # audit schema
    CREDENTIAL_CHECKED = Record('credential_checked', 'credential-checked-rule', 'request')
    # audit schema
    LOCKOUT_WRITTEN = Record('lockout_written', 'lockout-written-rule', 'audit')
    # audit schema
    LOCKOUT_DELETED = Record('lockout_deleted', 'lockout-deleted-rule', 'tenant')
    # audit schema
    REQUEST_STARTED = Record('request_started', 'request-started-rule', 'request')
    # audit schema
    REQUEST_FINISHED = Record('request_finished', 'request-finished-rule', 'audit')
    # audit schema
    STORE_ERROR = Record('store_error', 'store-error-rule', 'tenant')
    # audit schema
    CLOCK_ERROR = Record('clock_error', 'clock-error-rule', 'request')
    # audit schema
    POLICY_LOADED = Record('policy_loaded', 'policy-loaded-rule', 'audit')
    # audit schema
    ROUTE_SELECTED = Record('route_selected', 'route-selected-rule', 'tenant')
    # audit schema
    RESPONSE_SENT = Record('response_sent', 'response-sent-rule', 'request')
    # audit schema
    OPERATOR_OVERRIDE = Record('operator_override', 'operator-override-rule', 'audit')
    # audit schema
    RECOVERY_STARTED = Record('recovery_started', 'recovery-started-rule', 'tenant')
    # audit schema
    RECOVERY_FINISHED = Record('recovery_finished', 'recovery-finished-rule', 'request')
    # audit schema
    ACCOUNT_DISABLED = Record('account_disabled', 'account-disabled-rule', 'audit')
    # audit schema
    ACCOUNT_ENABLED = Record('account_enabled', 'account-enabled-rule', 'tenant')
    # audit schema
    SECRET_ROTATED = Record('secret_rotated', 'secret-rotated-rule', 'request')
    # audit schema
    TENANT_CREATED = Record('tenant_created', 'tenant-created-rule', 'audit')
    # audit schema
    TENANT_REMOVED = Record('tenant_removed', 'tenant-removed-rule', 'tenant')
    # audit schema
    CONFIGURATION_LOADED = Record('configuration_loaded', 'configuration-loaded-rule', 'request')
    # audit schema
    CONFIGURATION_REJECTED = Record('configuration_rejected', 'configuration-rejected-rule', 'audit')


def all_records():
    return (
        AUTH_FAILED,
        AUTH_BLOCKED,
        AUTH_SUCCEEDED,
        IDENTITY_NORMALIZED,
        CREDENTIAL_CHECKED,
        LOCKOUT_WRITTEN,
        LOCKOUT_DELETED,
        REQUEST_STARTED,
        REQUEST_FINISHED,
        STORE_ERROR,
        CLOCK_ERROR,
        POLICY_LOADED,
        ROUTE_SELECTED,
        RESPONSE_SENT,
        OPERATOR_OVERRIDE,
        RECOVERY_STARTED,
        RECOVERY_FINISHED,
        ACCOUNT_DISABLED,
        ACCOUNT_ENABLED,
        SECRET_ROTATED,
        TENANT_CREATED,
        TENANT_REMOVED,
        CONFIGURATION_LOADED,
        CONFIGURATION_REJECTED,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def event_for(value, records=None):
    item = select_event(value, records)
    return None if item is None else {"name": item.name, "value": item.value}


def select_event(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_security_event(value, records=None):
    return str(value).startswith("auth_") or str(value).startswith("lockout_")


def required_fields(value, records=None):
    return ("name", "identity", "at", "request_id")

