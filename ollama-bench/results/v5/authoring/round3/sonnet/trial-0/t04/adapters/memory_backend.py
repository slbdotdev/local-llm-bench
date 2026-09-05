from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # memory backend
    MEMORY_ACCOUNTS = Record('memory_accounts', 'memory-accounts-rule', 'tenant')
    # memory backend
    MEMORY_IDENTITIES = Record('memory_identities', 'memory-identities-rule', 'request')
    # memory backend
    MEMORY_LOCKOUTS = Record('memory_lockouts', 'memory-lockouts-rule', 'audit')
    # memory backend
    MEMORY_AUDIT = Record('memory_audit', 'memory-audit-rule', 'tenant')
    # memory backend
    MEMORY_POLICIES = Record('memory_policies', 'memory-policies-rule', 'request')
    # memory backend
    MEMORY_REQUESTS = Record('memory_requests', 'memory-requests-rule', 'audit')
    # memory backend
    MEMORY_SESSIONS = Record('memory_sessions', 'memory-sessions-rule', 'tenant')
    # memory backend
    MEMORY_TENANTS = Record('memory_tenants', 'memory-tenants-rule', 'request')
    # memory backend
    MEMORY_TRANSACTIONS = Record('memory_transactions', 'memory-transactions-rule', 'audit')
    # memory backend
    MEMORY_SNAPSHOTS = Record('memory_snapshots', 'memory-snapshots-rule', 'tenant')
    # memory backend
    MEMORY_RESTORE = Record('memory_restore', 'memory-restore-rule', 'request')
    # memory backend
    MEMORY_HEALTH = Record('memory_health', 'memory-health-rule', 'audit')
    # memory backend
    MEMORY_METRICS = Record('memory_metrics', 'memory-metrics-rule', 'tenant')
    # memory backend
    MEMORY_CLEANUP = Record('memory_cleanup', 'memory-cleanup-rule', 'request')
    # memory backend
    MEMORY_EXPIRY = Record('memory_expiry', 'memory-expiry-rule', 'audit')
    # memory backend
    MEMORY_COPY = Record('memory_copy', 'memory-copy-rule', 'tenant')
    # memory backend
    MEMORY_LOCK = Record('memory_lock', 'memory-lock-rule', 'request')
    # memory backend
    MEMORY_UNLOCK = Record('memory_unlock', 'memory-unlock-rule', 'audit')
    # memory backend
    MEMORY_WATCH = Record('memory_watch', 'memory-watch-rule', 'tenant')
    # memory backend
    MEMORY_UNWATCH = Record('memory_unwatch', 'memory-unwatch-rule', 'request')
    # memory backend
    MEMORY_NAMESPACE = Record('memory_namespace', 'memory-namespace-rule', 'audit')
    # memory backend
    MEMORY_CODEC = Record('memory_codec', 'memory-codec-rule', 'tenant')
    # memory backend
    MEMORY_ERRORS = Record('memory_errors', 'memory-errors-rule', 'request')
    # memory backend
    MEMORY_CAPACITY = Record('memory_capacity', 'memory-capacity-rule', 'audit')


def all_records():
    return (
        MEMORY_ACCOUNTS,
        MEMORY_IDENTITIES,
        MEMORY_LOCKOUTS,
        MEMORY_AUDIT,
        MEMORY_POLICIES,
        MEMORY_REQUESTS,
        MEMORY_SESSIONS,
        MEMORY_TENANTS,
        MEMORY_TRANSACTIONS,
        MEMORY_SNAPSHOTS,
        MEMORY_RESTORE,
        MEMORY_HEALTH,
        MEMORY_METRICS,
        MEMORY_CLEANUP,
        MEMORY_EXPIRY,
        MEMORY_COPY,
        MEMORY_LOCK,
        MEMORY_UNLOCK,
        MEMORY_WATCH,
        MEMORY_UNWATCH,
        MEMORY_NAMESPACE,
        MEMORY_CODEC,
        MEMORY_ERRORS,
        MEMORY_CAPACITY,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def table_for(value, records=None):
    item = select_table(value, records)
    return None if item is None else item.value


def select_table(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_ephemeral(value, records=None):
    return str(value).startswith("memory_")


def capacity(value, records=None):
    return {"items": 10000, "bytes": 10485760}

