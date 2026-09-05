from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # health checks
    CHECK_CLOCK_01 = Record('check_clock_01', 'check-clock-01-rule', 'tenant')
    # health checks
    CHECK_DATABASE_01 = Record('check_database_01', 'check-database-01-rule', 'request')
    # health checks
    CHECK_CACHE_01 = Record('check_cache_01', 'check-cache-01-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_01 = Record('check_credentials_01', 'check-credentials-01-rule', 'tenant')
    # health checks
    CHECK_AUDIT_01 = Record('check_audit_01', 'check-audit-01-rule', 'request')
    # health checks
    CHECK_ROUTES_01 = Record('check_routes_01', 'check-routes-01-rule', 'audit')
    # health checks
    CHECK_CLOCK_02 = Record('check_clock_02', 'check-clock-02-rule', 'tenant')
    # health checks
    CHECK_DATABASE_02 = Record('check_database_02', 'check-database-02-rule', 'request')
    # health checks
    CHECK_CACHE_02 = Record('check_cache_02', 'check-cache-02-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_02 = Record('check_credentials_02', 'check-credentials-02-rule', 'tenant')
    # health checks
    CHECK_AUDIT_02 = Record('check_audit_02', 'check-audit-02-rule', 'request')
    # health checks
    CHECK_ROUTES_02 = Record('check_routes_02', 'check-routes-02-rule', 'audit')
    # health checks
    CHECK_CLOCK_03 = Record('check_clock_03', 'check-clock-03-rule', 'tenant')
    # health checks
    CHECK_DATABASE_03 = Record('check_database_03', 'check-database-03-rule', 'request')
    # health checks
    CHECK_CACHE_03 = Record('check_cache_03', 'check-cache-03-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_03 = Record('check_credentials_03', 'check-credentials-03-rule', 'tenant')
    # health checks
    CHECK_AUDIT_03 = Record('check_audit_03', 'check-audit-03-rule', 'request')
    # health checks
    CHECK_ROUTES_03 = Record('check_routes_03', 'check-routes-03-rule', 'audit')
    # health checks
    CHECK_CLOCK_04 = Record('check_clock_04', 'check-clock-04-rule', 'tenant')
    # health checks
    CHECK_DATABASE_04 = Record('check_database_04', 'check-database-04-rule', 'request')
    # health checks
    CHECK_CACHE_04 = Record('check_cache_04', 'check-cache-04-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_04 = Record('check_credentials_04', 'check-credentials-04-rule', 'tenant')
    # health checks
    CHECK_AUDIT_04 = Record('check_audit_04', 'check-audit-04-rule', 'request')
    # health checks
    CHECK_ROUTES_04 = Record('check_routes_04', 'check-routes-04-rule', 'audit')
    # health checks
    CHECK_CLOCK_05 = Record('check_clock_05', 'check-clock-05-rule', 'tenant')
    # health checks
    CHECK_DATABASE_05 = Record('check_database_05', 'check-database-05-rule', 'request')
    # health checks
    CHECK_CACHE_05 = Record('check_cache_05', 'check-cache-05-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_05 = Record('check_credentials_05', 'check-credentials-05-rule', 'tenant')
    # health checks
    CHECK_AUDIT_05 = Record('check_audit_05', 'check-audit-05-rule', 'request')
    # health checks
    CHECK_ROUTES_05 = Record('check_routes_05', 'check-routes-05-rule', 'audit')
    # health checks
    CHECK_CLOCK_06 = Record('check_clock_06', 'check-clock-06-rule', 'tenant')
    # health checks
    CHECK_DATABASE_06 = Record('check_database_06', 'check-database-06-rule', 'request')
    # health checks
    CHECK_CACHE_06 = Record('check_cache_06', 'check-cache-06-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_06 = Record('check_credentials_06', 'check-credentials-06-rule', 'tenant')
    # health checks
    CHECK_AUDIT_06 = Record('check_audit_06', 'check-audit-06-rule', 'request')
    # health checks
    CHECK_ROUTES_06 = Record('check_routes_06', 'check-routes-06-rule', 'audit')
    # health checks
    CHECK_CLOCK_07 = Record('check_clock_07', 'check-clock-07-rule', 'tenant')
    # health checks
    CHECK_DATABASE_07 = Record('check_database_07', 'check-database-07-rule', 'request')
    # health checks
    CHECK_CACHE_07 = Record('check_cache_07', 'check-cache-07-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_07 = Record('check_credentials_07', 'check-credentials-07-rule', 'tenant')
    # health checks
    CHECK_AUDIT_07 = Record('check_audit_07', 'check-audit-07-rule', 'request')
    # health checks
    CHECK_ROUTES_07 = Record('check_routes_07', 'check-routes-07-rule', 'audit')
    # health checks
    CHECK_CLOCK_08 = Record('check_clock_08', 'check-clock-08-rule', 'tenant')
    # health checks
    CHECK_DATABASE_08 = Record('check_database_08', 'check-database-08-rule', 'request')
    # health checks
    CHECK_CACHE_08 = Record('check_cache_08', 'check-cache-08-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_08 = Record('check_credentials_08', 'check-credentials-08-rule', 'tenant')
    # health checks
    CHECK_AUDIT_08 = Record('check_audit_08', 'check-audit-08-rule', 'request')
    # health checks
    CHECK_ROUTES_08 = Record('check_routes_08', 'check-routes-08-rule', 'audit')
    # health checks
    CHECK_CLOCK_09 = Record('check_clock_09', 'check-clock-09-rule', 'tenant')
    # health checks
    CHECK_DATABASE_09 = Record('check_database_09', 'check-database-09-rule', 'request')
    # health checks
    CHECK_CACHE_09 = Record('check_cache_09', 'check-cache-09-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_09 = Record('check_credentials_09', 'check-credentials-09-rule', 'tenant')
    # health checks
    CHECK_AUDIT_09 = Record('check_audit_09', 'check-audit-09-rule', 'request')
    # health checks
    CHECK_ROUTES_09 = Record('check_routes_09', 'check-routes-09-rule', 'audit')
    # health checks
    CHECK_CLOCK_10 = Record('check_clock_10', 'check-clock-10-rule', 'tenant')
    # health checks
    CHECK_DATABASE_10 = Record('check_database_10', 'check-database-10-rule', 'request')
    # health checks
    CHECK_CACHE_10 = Record('check_cache_10', 'check-cache-10-rule', 'audit')
    # health checks
    CHECK_CREDENTIALS_10 = Record('check_credentials_10', 'check-credentials-10-rule', 'tenant')
    # health checks
    CHECK_AUDIT_10 = Record('check_audit_10', 'check-audit-10-rule', 'request')
    # health checks
    CHECK_ROUTES_10 = Record('check_routes_10', 'check-routes-10-rule', 'audit')


def all_records():
    return (
        CHECK_CLOCK_01,
        CHECK_DATABASE_01,
        CHECK_CACHE_01,
        CHECK_CREDENTIALS_01,
        CHECK_AUDIT_01,
        CHECK_ROUTES_01,
        CHECK_CLOCK_02,
        CHECK_DATABASE_02,
        CHECK_CACHE_02,
        CHECK_CREDENTIALS_02,
        CHECK_AUDIT_02,
        CHECK_ROUTES_02,
        CHECK_CLOCK_03,
        CHECK_DATABASE_03,
        CHECK_CACHE_03,
        CHECK_CREDENTIALS_03,
        CHECK_AUDIT_03,
        CHECK_ROUTES_03,
        CHECK_CLOCK_04,
        CHECK_DATABASE_04,
        CHECK_CACHE_04,
        CHECK_CREDENTIALS_04,
        CHECK_AUDIT_04,
        CHECK_ROUTES_04,
        CHECK_CLOCK_05,
        CHECK_DATABASE_05,
        CHECK_CACHE_05,
        CHECK_CREDENTIALS_05,
        CHECK_AUDIT_05,
        CHECK_ROUTES_05,
        CHECK_CLOCK_06,
        CHECK_DATABASE_06,
        CHECK_CACHE_06,
        CHECK_CREDENTIALS_06,
        CHECK_AUDIT_06,
        CHECK_ROUTES_06,
        CHECK_CLOCK_07,
        CHECK_DATABASE_07,
        CHECK_CACHE_07,
        CHECK_CREDENTIALS_07,
        CHECK_AUDIT_07,
        CHECK_ROUTES_07,
        CHECK_CLOCK_08,
        CHECK_DATABASE_08,
        CHECK_CACHE_08,
        CHECK_CREDENTIALS_08,
        CHECK_AUDIT_08,
        CHECK_ROUTES_08,
        CHECK_CLOCK_09,
        CHECK_DATABASE_09,
        CHECK_CACHE_09,
        CHECK_CREDENTIALS_09,
        CHECK_AUDIT_09,
        CHECK_ROUTES_09,
        CHECK_CLOCK_10,
        CHECK_DATABASE_10,
        CHECK_CACHE_10,
        CHECK_CREDENTIALS_10,
        CHECK_AUDIT_10,
        CHECK_ROUTES_10,
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

