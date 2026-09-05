from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # session paths
    SESSION_CREATE = Record('session_create', 'session-create-rule', 'tenant')
    # session paths
    SESSION_READ = Record('session_read', 'session-read-rule', 'request')
    # session paths
    SESSION_REFRESH = Record('session_refresh', 'session-refresh-rule', 'audit')
    # session paths
    SESSION_REVOKE = Record('session_revoke', 'session-revoke-rule', 'tenant')
    # session paths
    SESSION_EXPIRE = Record('session_expire', 'session-expire-rule', 'request')
    # session paths
    SESSION_ROTATE = Record('session_rotate', 'session-rotate-rule', 'audit')
    # session paths
    SESSION_COOKIE = Record('session_cookie', 'session-cookie-rule', 'tenant')
    # session paths
    SESSION_HEADER = Record('session_header', 'session-header-rule', 'request')
    # session paths
    SESSION_BINDING = Record('session_binding', 'session-binding-rule', 'audit')
    # session paths
    SESSION_DEVICE = Record('session_device', 'session-device-rule', 'tenant')
    # session paths
    SESSION_IP = Record('session_ip', 'session-ip-rule', 'request')
    # session paths
    SESSION_USER_AGENT = Record('session_user_agent', 'session-user-agent-rule', 'audit')
    # session paths
    SESSION_CSRF = Record('session_csrf', 'session-csrf-rule', 'tenant')
    # session paths
    SESSION_REPLAY = Record('session_replay', 'session-replay-rule', 'request')
    # session paths
    SESSION_STORE = Record('session_store', 'session-store-rule', 'audit')
    # session paths
    SESSION_CACHE = Record('session_cache', 'session-cache-rule', 'tenant')
    # session paths
    SESSION_METRICS = Record('session_metrics', 'session-metrics-rule', 'request')
    # session paths
    SESSION_AUDIT = Record('session_audit', 'session-audit-rule', 'audit')
    # session paths
    SESSION_CLEANUP = Record('session_cleanup', 'session-cleanup-rule', 'tenant')
    # session paths
    SESSION_HEALTH = Record('session_health', 'session-health-rule', 'request')
    # session paths
    SESSION_LIMITS = Record('session_limits', 'session-limits-rule', 'audit')
    # session paths
    SESSION_ERRORS = Record('session_errors', 'session-errors-rule', 'tenant')
    # session paths
    SESSION_CODEC = Record('session_codec', 'session-codec-rule', 'request')
    # session paths
    SESSION_KEYS = Record('session_keys', 'session-keys-rule', 'audit')


def all_records():
    return (
        SESSION_CREATE,
        SESSION_READ,
        SESSION_REFRESH,
        SESSION_REVOKE,
        SESSION_EXPIRE,
        SESSION_ROTATE,
        SESSION_COOKIE,
        SESSION_HEADER,
        SESSION_BINDING,
        SESSION_DEVICE,
        SESSION_IP,
        SESSION_USER_AGENT,
        SESSION_CSRF,
        SESSION_REPLAY,
        SESSION_STORE,
        SESSION_CACHE,
        SESSION_METRICS,
        SESSION_AUDIT,
        SESSION_CLEANUP,
        SESSION_HEALTH,
        SESSION_LIMITS,
        SESSION_ERRORS,
        SESSION_CODEC,
        SESSION_KEYS,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def path_for(value, records=None):
    item = select_path(value, records)
    return None if item is None else item.value


def select_path(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_identity_bound(value, records=None):
    return str(value) in {"session_binding", "session_device"}


def is_login_path(value, records=None):
    return str(value).startswith("session_") and str(value) in {"session_create", "session_refresh"}

