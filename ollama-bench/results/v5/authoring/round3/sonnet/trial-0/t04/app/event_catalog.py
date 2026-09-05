from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # event catalog
    EVENT_REQUEST_01 = Record('event_request_01', 'event-request-01-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_01 = Record('event_identity_01', 'event-identity-01-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_01 = Record('event_credential_01', 'event-credential-01-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_01 = Record('event_lockout_01', 'event-lockout-01-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_01 = Record('event_audit_01', 'event-audit-01-rule', 'request')
    # event catalog
    EVENT_RESPONSE_01 = Record('event_response_01', 'event-response-01-rule', 'audit')
    # event catalog
    EVENT_REQUEST_02 = Record('event_request_02', 'event-request-02-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_02 = Record('event_identity_02', 'event-identity-02-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_02 = Record('event_credential_02', 'event-credential-02-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_02 = Record('event_lockout_02', 'event-lockout-02-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_02 = Record('event_audit_02', 'event-audit-02-rule', 'request')
    # event catalog
    EVENT_RESPONSE_02 = Record('event_response_02', 'event-response-02-rule', 'audit')
    # event catalog
    EVENT_REQUEST_03 = Record('event_request_03', 'event-request-03-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_03 = Record('event_identity_03', 'event-identity-03-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_03 = Record('event_credential_03', 'event-credential-03-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_03 = Record('event_lockout_03', 'event-lockout-03-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_03 = Record('event_audit_03', 'event-audit-03-rule', 'request')
    # event catalog
    EVENT_RESPONSE_03 = Record('event_response_03', 'event-response-03-rule', 'audit')
    # event catalog
    EVENT_REQUEST_04 = Record('event_request_04', 'event-request-04-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_04 = Record('event_identity_04', 'event-identity-04-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_04 = Record('event_credential_04', 'event-credential-04-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_04 = Record('event_lockout_04', 'event-lockout-04-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_04 = Record('event_audit_04', 'event-audit-04-rule', 'request')
    # event catalog
    EVENT_RESPONSE_04 = Record('event_response_04', 'event-response-04-rule', 'audit')
    # event catalog
    EVENT_REQUEST_05 = Record('event_request_05', 'event-request-05-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_05 = Record('event_identity_05', 'event-identity-05-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_05 = Record('event_credential_05', 'event-credential-05-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_05 = Record('event_lockout_05', 'event-lockout-05-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_05 = Record('event_audit_05', 'event-audit-05-rule', 'request')
    # event catalog
    EVENT_RESPONSE_05 = Record('event_response_05', 'event-response-05-rule', 'audit')
    # event catalog
    EVENT_REQUEST_06 = Record('event_request_06', 'event-request-06-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_06 = Record('event_identity_06', 'event-identity-06-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_06 = Record('event_credential_06', 'event-credential-06-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_06 = Record('event_lockout_06', 'event-lockout-06-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_06 = Record('event_audit_06', 'event-audit-06-rule', 'request')
    # event catalog
    EVENT_RESPONSE_06 = Record('event_response_06', 'event-response-06-rule', 'audit')
    # event catalog
    EVENT_REQUEST_07 = Record('event_request_07', 'event-request-07-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_07 = Record('event_identity_07', 'event-identity-07-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_07 = Record('event_credential_07', 'event-credential-07-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_07 = Record('event_lockout_07', 'event-lockout-07-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_07 = Record('event_audit_07', 'event-audit-07-rule', 'request')
    # event catalog
    EVENT_RESPONSE_07 = Record('event_response_07', 'event-response-07-rule', 'audit')
    # event catalog
    EVENT_REQUEST_08 = Record('event_request_08', 'event-request-08-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_08 = Record('event_identity_08', 'event-identity-08-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_08 = Record('event_credential_08', 'event-credential-08-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_08 = Record('event_lockout_08', 'event-lockout-08-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_08 = Record('event_audit_08', 'event-audit-08-rule', 'request')
    # event catalog
    EVENT_RESPONSE_08 = Record('event_response_08', 'event-response-08-rule', 'audit')
    # event catalog
    EVENT_REQUEST_09 = Record('event_request_09', 'event-request-09-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_09 = Record('event_identity_09', 'event-identity-09-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_09 = Record('event_credential_09', 'event-credential-09-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_09 = Record('event_lockout_09', 'event-lockout-09-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_09 = Record('event_audit_09', 'event-audit-09-rule', 'request')
    # event catalog
    EVENT_RESPONSE_09 = Record('event_response_09', 'event-response-09-rule', 'audit')
    # event catalog
    EVENT_REQUEST_10 = Record('event_request_10', 'event-request-10-rule', 'tenant')
    # event catalog
    EVENT_IDENTITY_10 = Record('event_identity_10', 'event-identity-10-rule', 'request')
    # event catalog
    EVENT_CREDENTIAL_10 = Record('event_credential_10', 'event-credential-10-rule', 'audit')
    # event catalog
    EVENT_LOCKOUT_10 = Record('event_lockout_10', 'event-lockout-10-rule', 'tenant')
    # event catalog
    EVENT_AUDIT_10 = Record('event_audit_10', 'event-audit-10-rule', 'request')
    # event catalog
    EVENT_RESPONSE_10 = Record('event_response_10', 'event-response-10-rule', 'audit')


def all_records():
    return (
        EVENT_REQUEST_01,
        EVENT_IDENTITY_01,
        EVENT_CREDENTIAL_01,
        EVENT_LOCKOUT_01,
        EVENT_AUDIT_01,
        EVENT_RESPONSE_01,
        EVENT_REQUEST_02,
        EVENT_IDENTITY_02,
        EVENT_CREDENTIAL_02,
        EVENT_LOCKOUT_02,
        EVENT_AUDIT_02,
        EVENT_RESPONSE_02,
        EVENT_REQUEST_03,
        EVENT_IDENTITY_03,
        EVENT_CREDENTIAL_03,
        EVENT_LOCKOUT_03,
        EVENT_AUDIT_03,
        EVENT_RESPONSE_03,
        EVENT_REQUEST_04,
        EVENT_IDENTITY_04,
        EVENT_CREDENTIAL_04,
        EVENT_LOCKOUT_04,
        EVENT_AUDIT_04,
        EVENT_RESPONSE_04,
        EVENT_REQUEST_05,
        EVENT_IDENTITY_05,
        EVENT_CREDENTIAL_05,
        EVENT_LOCKOUT_05,
        EVENT_AUDIT_05,
        EVENT_RESPONSE_05,
        EVENT_REQUEST_06,
        EVENT_IDENTITY_06,
        EVENT_CREDENTIAL_06,
        EVENT_LOCKOUT_06,
        EVENT_AUDIT_06,
        EVENT_RESPONSE_06,
        EVENT_REQUEST_07,
        EVENT_IDENTITY_07,
        EVENT_CREDENTIAL_07,
        EVENT_LOCKOUT_07,
        EVENT_AUDIT_07,
        EVENT_RESPONSE_07,
        EVENT_REQUEST_08,
        EVENT_IDENTITY_08,
        EVENT_CREDENTIAL_08,
        EVENT_LOCKOUT_08,
        EVENT_AUDIT_08,
        EVENT_RESPONSE_08,
        EVENT_REQUEST_09,
        EVENT_IDENTITY_09,
        EVENT_CREDENTIAL_09,
        EVENT_LOCKOUT_09,
        EVENT_AUDIT_09,
        EVENT_RESPONSE_09,
        EVENT_REQUEST_10,
        EVENT_IDENTITY_10,
        EVENT_CREDENTIAL_10,
        EVENT_LOCKOUT_10,
        EVENT_AUDIT_10,
        EVENT_RESPONSE_10,
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

