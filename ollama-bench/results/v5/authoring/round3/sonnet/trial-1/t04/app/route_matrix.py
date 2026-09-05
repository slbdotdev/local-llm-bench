from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # route matrix
    ROUTE_LOGIN_01 = Record('route_login_01', 'route-login-01-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_01 = Record('route_health_01', 'route-health-01-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_01 = Record('route_logout_01', 'route-logout-01-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_01 = Record('route_recovery_01', 'route-recovery-01-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_01 = Record('route_admin_01', 'route-admin-01-rule', 'request')
    # route matrix
    ROUTE_METRICS_01 = Record('route_metrics_01', 'route-metrics-01-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_02 = Record('route_login_02', 'route-login-02-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_02 = Record('route_health_02', 'route-health-02-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_02 = Record('route_logout_02', 'route-logout-02-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_02 = Record('route_recovery_02', 'route-recovery-02-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_02 = Record('route_admin_02', 'route-admin-02-rule', 'request')
    # route matrix
    ROUTE_METRICS_02 = Record('route_metrics_02', 'route-metrics-02-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_03 = Record('route_login_03', 'route-login-03-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_03 = Record('route_health_03', 'route-health-03-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_03 = Record('route_logout_03', 'route-logout-03-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_03 = Record('route_recovery_03', 'route-recovery-03-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_03 = Record('route_admin_03', 'route-admin-03-rule', 'request')
    # route matrix
    ROUTE_METRICS_03 = Record('route_metrics_03', 'route-metrics-03-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_04 = Record('route_login_04', 'route-login-04-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_04 = Record('route_health_04', 'route-health-04-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_04 = Record('route_logout_04', 'route-logout-04-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_04 = Record('route_recovery_04', 'route-recovery-04-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_04 = Record('route_admin_04', 'route-admin-04-rule', 'request')
    # route matrix
    ROUTE_METRICS_04 = Record('route_metrics_04', 'route-metrics-04-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_05 = Record('route_login_05', 'route-login-05-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_05 = Record('route_health_05', 'route-health-05-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_05 = Record('route_logout_05', 'route-logout-05-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_05 = Record('route_recovery_05', 'route-recovery-05-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_05 = Record('route_admin_05', 'route-admin-05-rule', 'request')
    # route matrix
    ROUTE_METRICS_05 = Record('route_metrics_05', 'route-metrics-05-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_06 = Record('route_login_06', 'route-login-06-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_06 = Record('route_health_06', 'route-health-06-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_06 = Record('route_logout_06', 'route-logout-06-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_06 = Record('route_recovery_06', 'route-recovery-06-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_06 = Record('route_admin_06', 'route-admin-06-rule', 'request')
    # route matrix
    ROUTE_METRICS_06 = Record('route_metrics_06', 'route-metrics-06-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_07 = Record('route_login_07', 'route-login-07-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_07 = Record('route_health_07', 'route-health-07-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_07 = Record('route_logout_07', 'route-logout-07-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_07 = Record('route_recovery_07', 'route-recovery-07-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_07 = Record('route_admin_07', 'route-admin-07-rule', 'request')
    # route matrix
    ROUTE_METRICS_07 = Record('route_metrics_07', 'route-metrics-07-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_08 = Record('route_login_08', 'route-login-08-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_08 = Record('route_health_08', 'route-health-08-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_08 = Record('route_logout_08', 'route-logout-08-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_08 = Record('route_recovery_08', 'route-recovery-08-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_08 = Record('route_admin_08', 'route-admin-08-rule', 'request')
    # route matrix
    ROUTE_METRICS_08 = Record('route_metrics_08', 'route-metrics-08-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_09 = Record('route_login_09', 'route-login-09-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_09 = Record('route_health_09', 'route-health-09-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_09 = Record('route_logout_09', 'route-logout-09-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_09 = Record('route_recovery_09', 'route-recovery-09-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_09 = Record('route_admin_09', 'route-admin-09-rule', 'request')
    # route matrix
    ROUTE_METRICS_09 = Record('route_metrics_09', 'route-metrics-09-rule', 'audit')
    # route matrix
    ROUTE_LOGIN_10 = Record('route_login_10', 'route-login-10-rule', 'tenant')
    # route matrix
    ROUTE_HEALTH_10 = Record('route_health_10', 'route-health-10-rule', 'request')
    # route matrix
    ROUTE_LOGOUT_10 = Record('route_logout_10', 'route-logout-10-rule', 'audit')
    # route matrix
    ROUTE_RECOVERY_10 = Record('route_recovery_10', 'route-recovery-10-rule', 'tenant')
    # route matrix
    ROUTE_ADMIN_10 = Record('route_admin_10', 'route-admin-10-rule', 'request')
    # route matrix
    ROUTE_METRICS_10 = Record('route_metrics_10', 'route-metrics-10-rule', 'audit')


def all_records():
    return (
        ROUTE_LOGIN_01,
        ROUTE_HEALTH_01,
        ROUTE_LOGOUT_01,
        ROUTE_RECOVERY_01,
        ROUTE_ADMIN_01,
        ROUTE_METRICS_01,
        ROUTE_LOGIN_02,
        ROUTE_HEALTH_02,
        ROUTE_LOGOUT_02,
        ROUTE_RECOVERY_02,
        ROUTE_ADMIN_02,
        ROUTE_METRICS_02,
        ROUTE_LOGIN_03,
        ROUTE_HEALTH_03,
        ROUTE_LOGOUT_03,
        ROUTE_RECOVERY_03,
        ROUTE_ADMIN_03,
        ROUTE_METRICS_03,
        ROUTE_LOGIN_04,
        ROUTE_HEALTH_04,
        ROUTE_LOGOUT_04,
        ROUTE_RECOVERY_04,
        ROUTE_ADMIN_04,
        ROUTE_METRICS_04,
        ROUTE_LOGIN_05,
        ROUTE_HEALTH_05,
        ROUTE_LOGOUT_05,
        ROUTE_RECOVERY_05,
        ROUTE_ADMIN_05,
        ROUTE_METRICS_05,
        ROUTE_LOGIN_06,
        ROUTE_HEALTH_06,
        ROUTE_LOGOUT_06,
        ROUTE_RECOVERY_06,
        ROUTE_ADMIN_06,
        ROUTE_METRICS_06,
        ROUTE_LOGIN_07,
        ROUTE_HEALTH_07,
        ROUTE_LOGOUT_07,
        ROUTE_RECOVERY_07,
        ROUTE_ADMIN_07,
        ROUTE_METRICS_07,
        ROUTE_LOGIN_08,
        ROUTE_HEALTH_08,
        ROUTE_LOGOUT_08,
        ROUTE_RECOVERY_08,
        ROUTE_ADMIN_08,
        ROUTE_METRICS_08,
        ROUTE_LOGIN_09,
        ROUTE_HEALTH_09,
        ROUTE_LOGOUT_09,
        ROUTE_RECOVERY_09,
        ROUTE_ADMIN_09,
        ROUTE_METRICS_09,
        ROUTE_LOGIN_10,
        ROUTE_HEALTH_10,
        ROUTE_LOGOUT_10,
        ROUTE_RECOVERY_10,
        ROUTE_ADMIN_10,
        ROUTE_METRICS_10,
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

