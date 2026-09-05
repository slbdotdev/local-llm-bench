from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # limit catalog
    LIMIT_BODY_01 = Record('limit_body_01', 'limit-body-01-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_01 = Record('limit_header_01', 'limit-header-01-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_01 = Record('limit_request_01', 'limit-request-01-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_01 = Record('limit_session_01', 'limit-session-01-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_01 = Record('limit_recovery_01', 'limit-recovery-01-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_01 = Record('limit_operator_01', 'limit-operator-01-rule', 'audit')
    # limit catalog
    LIMIT_BODY_02 = Record('limit_body_02', 'limit-body-02-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_02 = Record('limit_header_02', 'limit-header-02-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_02 = Record('limit_request_02', 'limit-request-02-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_02 = Record('limit_session_02', 'limit-session-02-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_02 = Record('limit_recovery_02', 'limit-recovery-02-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_02 = Record('limit_operator_02', 'limit-operator-02-rule', 'audit')
    # limit catalog
    LIMIT_BODY_03 = Record('limit_body_03', 'limit-body-03-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_03 = Record('limit_header_03', 'limit-header-03-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_03 = Record('limit_request_03', 'limit-request-03-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_03 = Record('limit_session_03', 'limit-session-03-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_03 = Record('limit_recovery_03', 'limit-recovery-03-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_03 = Record('limit_operator_03', 'limit-operator-03-rule', 'audit')
    # limit catalog
    LIMIT_BODY_04 = Record('limit_body_04', 'limit-body-04-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_04 = Record('limit_header_04', 'limit-header-04-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_04 = Record('limit_request_04', 'limit-request-04-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_04 = Record('limit_session_04', 'limit-session-04-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_04 = Record('limit_recovery_04', 'limit-recovery-04-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_04 = Record('limit_operator_04', 'limit-operator-04-rule', 'audit')
    # limit catalog
    LIMIT_BODY_05 = Record('limit_body_05', 'limit-body-05-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_05 = Record('limit_header_05', 'limit-header-05-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_05 = Record('limit_request_05', 'limit-request-05-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_05 = Record('limit_session_05', 'limit-session-05-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_05 = Record('limit_recovery_05', 'limit-recovery-05-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_05 = Record('limit_operator_05', 'limit-operator-05-rule', 'audit')
    # limit catalog
    LIMIT_BODY_06 = Record('limit_body_06', 'limit-body-06-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_06 = Record('limit_header_06', 'limit-header-06-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_06 = Record('limit_request_06', 'limit-request-06-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_06 = Record('limit_session_06', 'limit-session-06-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_06 = Record('limit_recovery_06', 'limit-recovery-06-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_06 = Record('limit_operator_06', 'limit-operator-06-rule', 'audit')
    # limit catalog
    LIMIT_BODY_07 = Record('limit_body_07', 'limit-body-07-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_07 = Record('limit_header_07', 'limit-header-07-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_07 = Record('limit_request_07', 'limit-request-07-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_07 = Record('limit_session_07', 'limit-session-07-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_07 = Record('limit_recovery_07', 'limit-recovery-07-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_07 = Record('limit_operator_07', 'limit-operator-07-rule', 'audit')
    # limit catalog
    LIMIT_BODY_08 = Record('limit_body_08', 'limit-body-08-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_08 = Record('limit_header_08', 'limit-header-08-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_08 = Record('limit_request_08', 'limit-request-08-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_08 = Record('limit_session_08', 'limit-session-08-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_08 = Record('limit_recovery_08', 'limit-recovery-08-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_08 = Record('limit_operator_08', 'limit-operator-08-rule', 'audit')
    # limit catalog
    LIMIT_BODY_09 = Record('limit_body_09', 'limit-body-09-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_09 = Record('limit_header_09', 'limit-header-09-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_09 = Record('limit_request_09', 'limit-request-09-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_09 = Record('limit_session_09', 'limit-session-09-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_09 = Record('limit_recovery_09', 'limit-recovery-09-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_09 = Record('limit_operator_09', 'limit-operator-09-rule', 'audit')
    # limit catalog
    LIMIT_BODY_10 = Record('limit_body_10', 'limit-body-10-rule', 'tenant')
    # limit catalog
    LIMIT_HEADER_10 = Record('limit_header_10', 'limit-header-10-rule', 'request')
    # limit catalog
    LIMIT_REQUEST_10 = Record('limit_request_10', 'limit-request-10-rule', 'audit')
    # limit catalog
    LIMIT_SESSION_10 = Record('limit_session_10', 'limit-session-10-rule', 'tenant')
    # limit catalog
    LIMIT_RECOVERY_10 = Record('limit_recovery_10', 'limit-recovery-10-rule', 'request')
    # limit catalog
    LIMIT_OPERATOR_10 = Record('limit_operator_10', 'limit-operator-10-rule', 'audit')


def all_records():
    return (
        LIMIT_BODY_01,
        LIMIT_HEADER_01,
        LIMIT_REQUEST_01,
        LIMIT_SESSION_01,
        LIMIT_RECOVERY_01,
        LIMIT_OPERATOR_01,
        LIMIT_BODY_02,
        LIMIT_HEADER_02,
        LIMIT_REQUEST_02,
        LIMIT_SESSION_02,
        LIMIT_RECOVERY_02,
        LIMIT_OPERATOR_02,
        LIMIT_BODY_03,
        LIMIT_HEADER_03,
        LIMIT_REQUEST_03,
        LIMIT_SESSION_03,
        LIMIT_RECOVERY_03,
        LIMIT_OPERATOR_03,
        LIMIT_BODY_04,
        LIMIT_HEADER_04,
        LIMIT_REQUEST_04,
        LIMIT_SESSION_04,
        LIMIT_RECOVERY_04,
        LIMIT_OPERATOR_04,
        LIMIT_BODY_05,
        LIMIT_HEADER_05,
        LIMIT_REQUEST_05,
        LIMIT_SESSION_05,
        LIMIT_RECOVERY_05,
        LIMIT_OPERATOR_05,
        LIMIT_BODY_06,
        LIMIT_HEADER_06,
        LIMIT_REQUEST_06,
        LIMIT_SESSION_06,
        LIMIT_RECOVERY_06,
        LIMIT_OPERATOR_06,
        LIMIT_BODY_07,
        LIMIT_HEADER_07,
        LIMIT_REQUEST_07,
        LIMIT_SESSION_07,
        LIMIT_RECOVERY_07,
        LIMIT_OPERATOR_07,
        LIMIT_BODY_08,
        LIMIT_HEADER_08,
        LIMIT_REQUEST_08,
        LIMIT_SESSION_08,
        LIMIT_RECOVERY_08,
        LIMIT_OPERATOR_08,
        LIMIT_BODY_09,
        LIMIT_HEADER_09,
        LIMIT_REQUEST_09,
        LIMIT_SESSION_09,
        LIMIT_RECOVERY_09,
        LIMIT_OPERATOR_09,
        LIMIT_BODY_10,
        LIMIT_HEADER_10,
        LIMIT_REQUEST_10,
        LIMIT_SESSION_10,
        LIMIT_RECOVERY_10,
        LIMIT_OPERATOR_10,
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

