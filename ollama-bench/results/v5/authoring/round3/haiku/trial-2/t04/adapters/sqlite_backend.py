from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # sqlite backend
    SQLITE_ACCOUNTS = Record('sqlite_accounts', 'sqlite-accounts-rule', 'tenant')
    # sqlite backend
    SQLITE_IDENTITIES = Record('sqlite_identities', 'sqlite-identities-rule', 'request')
    # sqlite backend
    SQLITE_LOCKOUTS = Record('sqlite_lockouts', 'sqlite-lockouts-rule', 'audit')
    # sqlite backend
    SQLITE_AUDIT = Record('sqlite_audit', 'sqlite-audit-rule', 'tenant')
    # sqlite backend
    SQLITE_POLICIES = Record('sqlite_policies', 'sqlite-policies-rule', 'request')
    # sqlite backend
    SQLITE_REQUESTS = Record('sqlite_requests', 'sqlite-requests-rule', 'audit')
    # sqlite backend
    SQLITE_SESSIONS = Record('sqlite_sessions', 'sqlite-sessions-rule', 'tenant')
    # sqlite backend
    SQLITE_TENANTS = Record('sqlite_tenants', 'sqlite-tenants-rule', 'request')
    # sqlite backend
    SQLITE_INDEXES = Record('sqlite_indexes', 'sqlite-indexes-rule', 'audit')
    # sqlite backend
    SQLITE_TRANSACTIONS = Record('sqlite_transactions', 'sqlite-transactions-rule', 'tenant')
    # sqlite backend
    SQLITE_RETRIES = Record('sqlite_retries', 'sqlite-retries-rule', 'request')
    # sqlite backend
    SQLITE_CONNECTIONS = Record('sqlite_connections', 'sqlite-connections-rule', 'audit')
    # sqlite backend
    SQLITE_PRAGMAS = Record('sqlite_pragmas', 'sqlite-pragmas-rule', 'tenant')
    # sqlite backend
    SQLITE_BACKUP = Record('sqlite_backup', 'sqlite-backup-rule', 'request')
    # sqlite backend
    SQLITE_RESTORE = Record('sqlite_restore', 'sqlite-restore-rule', 'audit')
    # sqlite backend
    SQLITE_HEALTH = Record('sqlite_health', 'sqlite-health-rule', 'tenant')
    # sqlite backend
    SQLITE_METRICS = Record('sqlite_metrics', 'sqlite-metrics-rule', 'request')
    # sqlite backend
    SQLITE_CLEANUP = Record('sqlite_cleanup', 'sqlite-cleanup-rule', 'audit')
    # sqlite backend
    SQLITE_VACUUM = Record('sqlite_vacuum', 'sqlite-vacuum-rule', 'tenant')
    # sqlite backend
    SQLITE_MIGRATIONS = Record('sqlite_migrations', 'sqlite-migrations-rule', 'request')
    # sqlite backend
    SQLITE_ENCODING = Record('sqlite_encoding', 'sqlite-encoding-rule', 'audit')
    # sqlite backend
    SQLITE_BUSY_TIMEOUT = Record('sqlite_busy_timeout', 'sqlite-busy-timeout-rule', 'tenant')
    # sqlite backend
    SQLITE_READONLY = Record('sqlite_readonly', 'sqlite-readonly-rule', 'request')
    # sqlite backend
    SQLITE_POOL = Record('sqlite_pool', 'sqlite-pool-rule', 'audit')


def all_records():
    return (
        SQLITE_ACCOUNTS,
        SQLITE_IDENTITIES,
        SQLITE_LOCKOUTS,
        SQLITE_AUDIT,
        SQLITE_POLICIES,
        SQLITE_REQUESTS,
        SQLITE_SESSIONS,
        SQLITE_TENANTS,
        SQLITE_INDEXES,
        SQLITE_TRANSACTIONS,
        SQLITE_RETRIES,
        SQLITE_CONNECTIONS,
        SQLITE_PRAGMAS,
        SQLITE_BACKUP,
        SQLITE_RESTORE,
        SQLITE_HEALTH,
        SQLITE_METRICS,
        SQLITE_CLEANUP,
        SQLITE_VACUUM,
        SQLITE_MIGRATIONS,
        SQLITE_ENCODING,
        SQLITE_BUSY_TIMEOUT,
        SQLITE_READONLY,
        SQLITE_POOL,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def table_for(value, records=None):
    item = select_table(value, records)
    return None if item is None else item.value


def select_table(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_durable(value, records=None):
    return str(value) in {"sqlite_lockouts", "sqlite_accounts", "sqlite_audit"}


def connection_options(value, records=None):
    return {"timeout": 5, "isolation_level": "IMMEDIATE"}

