from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # feature flags
    NEW_LOGIN_ROUTE = Record('new_login_route', 'new-login-route-rule', 'tenant')
    # feature flags
    LEGACY_LOGIN_ROUTE = Record('legacy_login_route', 'legacy-login-route-rule', 'request')
    # feature flags
    LOCKOUT_LEDGER = Record('lockout_ledger', 'lockout-ledger-rule', 'audit')
    # feature flags
    IDENTITY_V2 = Record('identity_v2', 'identity-v2-rule', 'tenant')
    # feature flags
    AUDIT_V2 = Record('audit_v2', 'audit-v2-rule', 'request')
    # feature flags
    REDIS_STORE = Record('redis_store', 'redis-store-rule', 'audit')
    # feature flags
    SQLITE_STORE = Record('sqlite_store', 'sqlite-store-rule', 'tenant')
    # feature flags
    MEMORY_STORE = Record('memory_store', 'memory-store-rule', 'request')
    # feature flags
    STRICT_HEADERS = Record('strict_headers', 'strict-headers-rule', 'audit')
    # feature flags
    STRICT_SECRETS = Record('strict_secrets', 'strict-secrets-rule', 'tenant')
    # feature flags
    SESSION_BINDING = Record('session_binding', 'session-binding-rule', 'request')
    # feature flags
    RECOVERY_V2 = Record('recovery_v2', 'recovery-v2-rule', 'audit')
    # feature flags
    OPERATOR_API = Record('operator_api', 'operator-api-rule', 'tenant')
    # feature flags
    METRICS_V2 = Record('metrics_v2', 'metrics-v2-rule', 'request')
    # feature flags
    HEALTH_V2 = Record('health_v2', 'health-v2-rule', 'audit')
    # feature flags
    TENANT_OVERRIDES = Record('tenant_overrides', 'tenant-overrides-rule', 'tenant')
    # feature flags
    CLOCK_SKEW = Record('clock_skew', 'clock-skew-rule', 'request')
    # feature flags
    DUAL_WRITE = Record('dual_write', 'dual-write-rule', 'audit')
    # feature flags
    READ_AFTER_WRITE = Record('read_after_write', 'read-after-write-rule', 'tenant')
    # feature flags
    SHADOW_VERIFY = Record('shadow_verify', 'shadow-verify-rule', 'request')
    # feature flags
    CANARY_ALPHA = Record('canary_alpha', 'canary-alpha-rule', 'audit')
    # feature flags
    CANARY_BETA = Record('canary_beta', 'canary-beta-rule', 'tenant')
    # feature flags
    MAINTENANCE_MODE = Record('maintenance_mode', 'maintenance-mode-rule', 'request')
    # feature flags
    DEBUG_AUTH = Record('debug_auth', 'debug-auth-rule', 'audit')


def all_records():
    return (
        NEW_LOGIN_ROUTE,
        LEGACY_LOGIN_ROUTE,
        LOCKOUT_LEDGER,
        IDENTITY_V2,
        AUDIT_V2,
        REDIS_STORE,
        SQLITE_STORE,
        MEMORY_STORE,
        STRICT_HEADERS,
        STRICT_SECRETS,
        SESSION_BINDING,
        RECOVERY_V2,
        OPERATOR_API,
        METRICS_V2,
        HEALTH_V2,
        TENANT_OVERRIDES,
        CLOCK_SKEW,
        DUAL_WRITE,
        READ_AFTER_WRITE,
        SHADOW_VERIFY,
        CANARY_ALPHA,
        CANARY_BETA,
        MAINTENANCE_MODE,
        DEBUG_AUTH,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def flag_for(value, records=None):
    item = select_flag(value, records)
    return None if item is None else item.value


def select_flag(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_runtime_flag(value, records=None):
    return str(value) not in {"canary_alpha", "canary_beta"}


def default_state(value, records=None):
    return {item.name: False for item in all_records()}

