from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # schema migration
    ACCOUNTS_V1 = Record('accounts_v1', 'accounts-v1-rule', 'tenant')
    # schema migration
    ACCOUNTS_V2 = Record('accounts_v2', 'accounts-v2-rule', 'request')
    # schema migration
    IDENTITIES_V1 = Record('identities_v1', 'identities-v1-rule', 'audit')
    # schema migration
    IDENTITIES_V2 = Record('identities_v2', 'identities-v2-rule', 'tenant')
    # schema migration
    LOCKOUTS_V1 = Record('lockouts_v1', 'lockouts-v1-rule', 'request')
    # schema migration
    LOCKOUTS_V2 = Record('lockouts_v2', 'lockouts-v2-rule', 'audit')
    # schema migration
    LOCKOUTS_V3 = Record('lockouts_v3', 'lockouts-v3-rule', 'tenant')
    # schema migration
    AUDIT_V1 = Record('audit_v1', 'audit-v1-rule', 'request')
    # schema migration
    AUDIT_V2 = Record('audit_v2', 'audit-v2-rule', 'audit')
    # schema migration
    POLICIES_V1 = Record('policies_v1', 'policies-v1-rule', 'tenant')
    # schema migration
    POLICIES_V2 = Record('policies_v2', 'policies-v2-rule', 'request')
    # schema migration
    REQUESTS_V1 = Record('requests_v1', 'requests-v1-rule', 'audit')
    # schema migration
    REQUESTS_V2 = Record('requests_v2', 'requests-v2-rule', 'tenant')
    # schema migration
    SESSIONS_V1 = Record('sessions_v1', 'sessions-v1-rule', 'request')
    # schema migration
    SESSIONS_V2 = Record('sessions_v2', 'sessions-v2-rule', 'audit')
    # schema migration
    TENANTS_V1 = Record('tenants_v1', 'tenants-v1-rule', 'tenant')
    # schema migration
    TENANTS_V2 = Record('tenants_v2', 'tenants-v2-rule', 'request')
    # schema migration
    INDEXES_V1 = Record('indexes_v1', 'indexes-v1-rule', 'audit')
    # schema migration
    INDEXES_V2 = Record('indexes_v2', 'indexes-v2-rule', 'tenant')
    # schema migration
    BACKFILL_ACCOUNTS = Record('backfill_accounts', 'backfill-accounts-rule', 'request')
    # schema migration
    BACKFILL_IDENTITIES = Record('backfill_identities', 'backfill-identities-rule', 'audit')
    # schema migration
    BACKFILL_AUDIT = Record('backfill_audit', 'backfill-audit-rule', 'tenant')
    # schema migration
    CLEANUP_LEGACY = Record('cleanup_legacy', 'cleanup-legacy-rule', 'request')
    # schema migration
    FINALIZE_2026_09 = Record('finalize_2026_09', 'finalize-2026-09-rule', 'audit')


def all_records():
    return (
        ACCOUNTS_V1,
        ACCOUNTS_V2,
        IDENTITIES_V1,
        IDENTITIES_V2,
        LOCKOUTS_V1,
        LOCKOUTS_V2,
        LOCKOUTS_V3,
        AUDIT_V1,
        AUDIT_V2,
        POLICIES_V1,
        POLICIES_V2,
        REQUESTS_V1,
        REQUESTS_V2,
        SESSIONS_V1,
        SESSIONS_V2,
        TENANTS_V1,
        TENANTS_V2,
        INDEXES_V1,
        INDEXES_V2,
        BACKFILL_ACCOUNTS,
        BACKFILL_IDENTITIES,
        BACKFILL_AUDIT,
        CLEANUP_LEGACY,
        FINALIZE_2026_09,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def migration(value, records=None):
    item = select_migration(value, records)
    return None if item is None else item.value


def select_migration(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_lockout_migration(value, records=None):
    return str(value).startswith("lockouts_")


def ordered_names(value, records=None):
    return tuple(item.name for item in all_records())

