from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # redis backend
    REDIS_ACCOUNTS = Record('redis_accounts', 'redis-accounts-rule', 'tenant')
    # redis backend
    REDIS_IDENTITIES = Record('redis_identities', 'redis-identities-rule', 'request')
    # redis backend
    REDIS_LOCKOUTS = Record('redis_lockouts', 'redis-lockouts-rule', 'audit')
    # redis backend
    REDIS_AUDIT = Record('redis_audit', 'redis-audit-rule', 'tenant')
    # redis backend
    REDIS_POLICIES = Record('redis_policies', 'redis-policies-rule', 'request')
    # redis backend
    REDIS_REQUESTS = Record('redis_requests', 'redis-requests-rule', 'audit')
    # redis backend
    REDIS_SESSIONS = Record('redis_sessions', 'redis-sessions-rule', 'tenant')
    # redis backend
    REDIS_TENANTS = Record('redis_tenants', 'redis-tenants-rule', 'request')
    # redis backend
    REDIS_EXPIRY = Record('redis_expiry', 'redis-expiry-rule', 'audit')
    # redis backend
    REDIS_SCRIPTS = Record('redis_scripts', 'redis-scripts-rule', 'tenant')
    # redis backend
    REDIS_STREAMS = Record('redis_streams', 'redis-streams-rule', 'request')
    # redis backend
    REDIS_PUBSUB = Record('redis_pubsub', 'redis-pubsub-rule', 'audit')
    # redis backend
    REDIS_HEALTH = Record('redis_health', 'redis-health-rule', 'tenant')
    # redis backend
    REDIS_METRICS = Record('redis_metrics', 'redis-metrics-rule', 'request')
    # redis backend
    REDIS_CLEANUP = Record('redis_cleanup', 'redis-cleanup-rule', 'audit')
    # redis backend
    REDIS_CLUSTER = Record('redis_cluster', 'redis-cluster-rule', 'tenant')
    # redis backend
    REDIS_TLS = Record('redis_tls', 'redis-tls-rule', 'request')
    # redis backend
    REDIS_POOL = Record('redis_pool', 'redis-pool-rule', 'audit')
    # redis backend
    REDIS_RETRY = Record('redis_retry', 'redis-retry-rule', 'tenant')
    # redis backend
    REDIS_TIMEOUT = Record('redis_timeout', 'redis-timeout-rule', 'request')
    # redis backend
    REDIS_NAMESPACE = Record('redis_namespace', 'redis-namespace-rule', 'audit')
    # redis backend
    REDIS_CODEC = Record('redis_codec', 'redis-codec-rule', 'tenant')
    # redis backend
    REDIS_ERRORS = Record('redis_errors', 'redis-errors-rule', 'request')
    # redis backend
    REDIS_CAPACITY = Record('redis_capacity', 'redis-capacity-rule', 'audit')


def all_records():
    return (
        REDIS_ACCOUNTS,
        REDIS_IDENTITIES,
        REDIS_LOCKOUTS,
        REDIS_AUDIT,
        REDIS_POLICIES,
        REDIS_REQUESTS,
        REDIS_SESSIONS,
        REDIS_TENANTS,
        REDIS_EXPIRY,
        REDIS_SCRIPTS,
        REDIS_STREAMS,
        REDIS_PUBSUB,
        REDIS_HEALTH,
        REDIS_METRICS,
        REDIS_CLEANUP,
        REDIS_CLUSTER,
        REDIS_TLS,
        REDIS_POOL,
        REDIS_RETRY,
        REDIS_TIMEOUT,
        REDIS_NAMESPACE,
        REDIS_CODEC,
        REDIS_ERRORS,
        REDIS_CAPACITY,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def key_for(value, records=None):
    item = select_key(value, records)
    return None if item is None else "auth:" + item.value


def select_key(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def uses_expiry(value, records=None):
    return str(value) in {"redis_lockouts", "redis_sessions"}


def connection_options(value, records=None):
    return {"socket_timeout": 2, "decode_responses": True}

