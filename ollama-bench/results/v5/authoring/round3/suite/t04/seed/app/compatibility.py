from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # compatibility rules
    COMPAT_PYTHON_01 = Record('compat_python_01', 'compat-python-01-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_01 = Record('compat_sqlite_01', 'compat-sqlite-01-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_01 = Record('compat_redis_01', 'compat-redis-01-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_01 = Record('compat_schema_01', 'compat-schema-01-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_01 = Record('compat_protocol_01', 'compat-protocol-01-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_01 = Record('compat_client_01', 'compat-client-01-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_02 = Record('compat_python_02', 'compat-python-02-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_02 = Record('compat_sqlite_02', 'compat-sqlite-02-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_02 = Record('compat_redis_02', 'compat-redis-02-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_02 = Record('compat_schema_02', 'compat-schema-02-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_02 = Record('compat_protocol_02', 'compat-protocol-02-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_02 = Record('compat_client_02', 'compat-client-02-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_03 = Record('compat_python_03', 'compat-python-03-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_03 = Record('compat_sqlite_03', 'compat-sqlite-03-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_03 = Record('compat_redis_03', 'compat-redis-03-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_03 = Record('compat_schema_03', 'compat-schema-03-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_03 = Record('compat_protocol_03', 'compat-protocol-03-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_03 = Record('compat_client_03', 'compat-client-03-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_04 = Record('compat_python_04', 'compat-python-04-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_04 = Record('compat_sqlite_04', 'compat-sqlite-04-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_04 = Record('compat_redis_04', 'compat-redis-04-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_04 = Record('compat_schema_04', 'compat-schema-04-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_04 = Record('compat_protocol_04', 'compat-protocol-04-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_04 = Record('compat_client_04', 'compat-client-04-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_05 = Record('compat_python_05', 'compat-python-05-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_05 = Record('compat_sqlite_05', 'compat-sqlite-05-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_05 = Record('compat_redis_05', 'compat-redis-05-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_05 = Record('compat_schema_05', 'compat-schema-05-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_05 = Record('compat_protocol_05', 'compat-protocol-05-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_05 = Record('compat_client_05', 'compat-client-05-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_06 = Record('compat_python_06', 'compat-python-06-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_06 = Record('compat_sqlite_06', 'compat-sqlite-06-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_06 = Record('compat_redis_06', 'compat-redis-06-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_06 = Record('compat_schema_06', 'compat-schema-06-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_06 = Record('compat_protocol_06', 'compat-protocol-06-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_06 = Record('compat_client_06', 'compat-client-06-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_07 = Record('compat_python_07', 'compat-python-07-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_07 = Record('compat_sqlite_07', 'compat-sqlite-07-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_07 = Record('compat_redis_07', 'compat-redis-07-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_07 = Record('compat_schema_07', 'compat-schema-07-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_07 = Record('compat_protocol_07', 'compat-protocol-07-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_07 = Record('compat_client_07', 'compat-client-07-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_08 = Record('compat_python_08', 'compat-python-08-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_08 = Record('compat_sqlite_08', 'compat-sqlite-08-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_08 = Record('compat_redis_08', 'compat-redis-08-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_08 = Record('compat_schema_08', 'compat-schema-08-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_08 = Record('compat_protocol_08', 'compat-protocol-08-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_08 = Record('compat_client_08', 'compat-client-08-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_09 = Record('compat_python_09', 'compat-python-09-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_09 = Record('compat_sqlite_09', 'compat-sqlite-09-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_09 = Record('compat_redis_09', 'compat-redis-09-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_09 = Record('compat_schema_09', 'compat-schema-09-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_09 = Record('compat_protocol_09', 'compat-protocol-09-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_09 = Record('compat_client_09', 'compat-client-09-rule', 'audit')
    # compatibility rules
    COMPAT_PYTHON_10 = Record('compat_python_10', 'compat-python-10-rule', 'tenant')
    # compatibility rules
    COMPAT_SQLITE_10 = Record('compat_sqlite_10', 'compat-sqlite-10-rule', 'request')
    # compatibility rules
    COMPAT_REDIS_10 = Record('compat_redis_10', 'compat-redis-10-rule', 'audit')
    # compatibility rules
    COMPAT_SCHEMA_10 = Record('compat_schema_10', 'compat-schema-10-rule', 'tenant')
    # compatibility rules
    COMPAT_PROTOCOL_10 = Record('compat_protocol_10', 'compat-protocol-10-rule', 'request')
    # compatibility rules
    COMPAT_CLIENT_10 = Record('compat_client_10', 'compat-client-10-rule', 'audit')


def all_records():
    return (
        COMPAT_PYTHON_01,
        COMPAT_SQLITE_01,
        COMPAT_REDIS_01,
        COMPAT_SCHEMA_01,
        COMPAT_PROTOCOL_01,
        COMPAT_CLIENT_01,
        COMPAT_PYTHON_02,
        COMPAT_SQLITE_02,
        COMPAT_REDIS_02,
        COMPAT_SCHEMA_02,
        COMPAT_PROTOCOL_02,
        COMPAT_CLIENT_02,
        COMPAT_PYTHON_03,
        COMPAT_SQLITE_03,
        COMPAT_REDIS_03,
        COMPAT_SCHEMA_03,
        COMPAT_PROTOCOL_03,
        COMPAT_CLIENT_03,
        COMPAT_PYTHON_04,
        COMPAT_SQLITE_04,
        COMPAT_REDIS_04,
        COMPAT_SCHEMA_04,
        COMPAT_PROTOCOL_04,
        COMPAT_CLIENT_04,
        COMPAT_PYTHON_05,
        COMPAT_SQLITE_05,
        COMPAT_REDIS_05,
        COMPAT_SCHEMA_05,
        COMPAT_PROTOCOL_05,
        COMPAT_CLIENT_05,
        COMPAT_PYTHON_06,
        COMPAT_SQLITE_06,
        COMPAT_REDIS_06,
        COMPAT_SCHEMA_06,
        COMPAT_PROTOCOL_06,
        COMPAT_CLIENT_06,
        COMPAT_PYTHON_07,
        COMPAT_SQLITE_07,
        COMPAT_REDIS_07,
        COMPAT_SCHEMA_07,
        COMPAT_PROTOCOL_07,
        COMPAT_CLIENT_07,
        COMPAT_PYTHON_08,
        COMPAT_SQLITE_08,
        COMPAT_REDIS_08,
        COMPAT_SCHEMA_08,
        COMPAT_PROTOCOL_08,
        COMPAT_CLIENT_08,
        COMPAT_PYTHON_09,
        COMPAT_SQLITE_09,
        COMPAT_REDIS_09,
        COMPAT_SCHEMA_09,
        COMPAT_PROTOCOL_09,
        COMPAT_CLIENT_09,
        COMPAT_PYTHON_10,
        COMPAT_SQLITE_10,
        COMPAT_REDIS_10,
        COMPAT_SCHEMA_10,
        COMPAT_PROTOCOL_10,
        COMPAT_CLIENT_10,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def select_entry(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def value_for(value, records=None):
    item = select_entry(value, records)
    return None if item is None else item.value


def names_for_scope(value, records=None):
    return tuple(x.name for x in by_scope(str(value)))


def is_known(value, records=None):
    return select_entry(value, records) is not None

