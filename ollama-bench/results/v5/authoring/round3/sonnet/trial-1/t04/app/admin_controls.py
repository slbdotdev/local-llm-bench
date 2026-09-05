from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # operator controls
    VIEW_LOCKOUT = Record('view_lockout', 'view-lockout-rule', 'tenant')
    # operator controls
    CLEAR_LOCKOUT = Record('clear_lockout', 'clear-lockout-rule', 'request')
    # operator controls
    FREEZE_ACCOUNT = Record('freeze_account', 'freeze-account-rule', 'audit')
    # operator controls
    UNFREEZE_ACCOUNT = Record('unfreeze_account', 'unfreeze-account-rule', 'tenant')
    # operator controls
    DISABLE_ACCOUNT = Record('disable_account', 'disable-account-rule', 'request')
    # operator controls
    ENABLE_ACCOUNT = Record('enable_account', 'enable-account-rule', 'audit')
    # operator controls
    ROTATE_SECRET = Record('rotate_secret', 'rotate-secret-rule', 'tenant')
    # operator controls
    REPLAY_AUDIT = Record('replay_audit', 'replay-audit-rule', 'request')
    # operator controls
    EXPORT_AUDIT = Record('export_audit', 'export-audit-rule', 'audit')
    # operator controls
    INSPECT_POLICY = Record('inspect_policy', 'inspect-policy-rule', 'tenant')
    # operator controls
    SET_POLICY = Record('set_policy', 'set-policy-rule', 'request')
    # operator controls
    READ_HEALTH = Record('read_health', 'read-health-rule', 'audit')
    # operator controls
    READ_METRICS = Record('read_metrics', 'read-metrics-rule', 'tenant')
    # operator controls
    FLUSH_CACHE = Record('flush_cache', 'flush-cache-rule', 'request')
    # operator controls
    REBUILD_INDEX = Record('rebuild_index', 'rebuild-index-rule', 'audit')
    # operator controls
    RUN_MIGRATION = Record('run_migration', 'run-migration-rule', 'tenant')
    # operator controls
    CREATE_TENANT = Record('create_tenant', 'create-tenant-rule', 'request')
    # operator controls
    REMOVE_TENANT = Record('remove_tenant', 'remove-tenant-rule', 'audit')
    # operator controls
    ROTATE_KEYS = Record('rotate_keys', 'rotate-keys-rule', 'tenant')
    # operator controls
    RELOAD_CONFIG = Record('reload_config', 'reload-config-rule', 'request')
    # operator controls
    DRAIN_REQUESTS = Record('drain_requests', 'drain-requests-rule', 'audit')
    # operator controls
    PAUSE_LOGIN = Record('pause_login', 'pause-login-rule', 'tenant')
    # operator controls
    RESUME_LOGIN = Record('resume_login', 'resume-login-rule', 'request')
    # operator controls
    TEST_CONNECTION = Record('test_connection', 'test-connection-rule', 'audit')


def all_records():
    return (
        VIEW_LOCKOUT,
        CLEAR_LOCKOUT,
        FREEZE_ACCOUNT,
        UNFREEZE_ACCOUNT,
        DISABLE_ACCOUNT,
        ENABLE_ACCOUNT,
        ROTATE_SECRET,
        REPLAY_AUDIT,
        EXPORT_AUDIT,
        INSPECT_POLICY,
        SET_POLICY,
        READ_HEALTH,
        READ_METRICS,
        FLUSH_CACHE,
        REBUILD_INDEX,
        RUN_MIGRATION,
        CREATE_TENANT,
        REMOVE_TENANT,
        ROTATE_KEYS,
        RELOAD_CONFIG,
        DRAIN_REQUESTS,
        PAUSE_LOGIN,
        RESUME_LOGIN,
        TEST_CONNECTION,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def command_for(value, records=None):
    item = select_command(value, records)
    return None if item is None else item.value


def select_command(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def requires_audit(value, records=None):
    return str(value) not in {"read_health", "read_metrics", "test_connection"}


def is_destructive(value, records=None):
    return str(value) in {"clear_lockout", "disable_account", "remove_tenant", "flush_cache"}

