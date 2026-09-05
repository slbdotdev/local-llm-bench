from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # adapter contract
    GET_LOCK = Record('get_lock', 'get-lock-rule', 'tenant')
    # adapter contract
    PUT_LOCK = Record('put_lock', 'put-lock-rule', 'request')
    # adapter contract
    DELETE_LOCK = Record('delete_lock', 'delete-lock-rule', 'audit')
    # adapter contract
    SCAN_LOCKS = Record('scan_locks', 'scan-locks-rule', 'tenant')
    # adapter contract
    BEGIN = Record('begin', 'begin-rule', 'request')
    # adapter contract
    COMMIT = Record('commit', 'commit-rule', 'audit')
    # adapter contract
    ROLLBACK = Record('rollback', 'rollback-rule', 'tenant')
    # adapter contract
    HEALTH = Record('health', 'health-rule', 'request')
    # adapter contract
    CLOSE = Record('close', 'close-rule', 'audit')
    # adapter contract
    READ_ACCOUNT = Record('read_account', 'read-account-rule', 'tenant')
    # adapter contract
    WRITE_ACCOUNT = Record('write_account', 'write-account-rule', 'request')
    # adapter contract
    DELETE_ACCOUNT = Record('delete_account', 'delete-account-rule', 'audit')
    # adapter contract
    READ_POLICY = Record('read_policy', 'read-policy-rule', 'tenant')
    # adapter contract
    WRITE_POLICY = Record('write_policy', 'write-policy-rule', 'request')
    # adapter contract
    APPEND_AUDIT = Record('append_audit', 'append-audit-rule', 'audit')
    # adapter contract
    READ_AUDIT = Record('read_audit', 'read-audit-rule', 'tenant')
    # adapter contract
    CLOCK_NOW = Record('clock_now', 'clock-now-rule', 'request')
    # adapter contract
    CLOCK_MONOTONIC = Record('clock_monotonic', 'clock-monotonic-rule', 'audit')
    # adapter contract
    PING = Record('ping', 'ping-rule', 'tenant')
    # adapter contract
    METRICS = Record('metrics', 'metrics-rule', 'request')
    # adapter contract
    TRANSACTION = Record('transaction', 'transaction-rule', 'audit')
    # adapter contract
    BACKUP = Record('backup', 'backup-rule', 'tenant')
    # adapter contract
    RESTORE = Record('restore', 'restore-rule', 'request')


def all_records():
    return (
        GET_LOCK,
        PUT_LOCK,
        DELETE_LOCK,
        SCAN_LOCKS,
        BEGIN,
        COMMIT,
        ROLLBACK,
        HEALTH,
        CLOSE,
        READ_ACCOUNT,
        WRITE_ACCOUNT,
        DELETE_ACCOUNT,
        READ_POLICY,
        WRITE_POLICY,
        APPEND_AUDIT,
        READ_AUDIT,
        CLOCK_NOW,
        CLOCK_MONOTONIC,
        PING,
        METRICS,
        TRANSACTION,
        BACKUP,
        RESTORE,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def select_operation(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_mutating(value, records=None):
    item = select_operation(value, records)
    return item is not None and item.name in {"put_lock", "delete_lock", "write_account", "write_policy"}


def operation_names(value, records=None):
    return tuple(item.name for item in all_records())


def contract_version(value, records=None):
    return "2026-08"

