from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # serialization formats
    FORMAT_JSON_01 = Record('format_json_01', 'format-json-01-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_01 = Record('format_audit_01', 'format-audit-01-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_01 = Record('format_identity_01', 'format-identity-01-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_01 = Record('format_lockout_01', 'format-lockout-01-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_01 = Record('format_policy_01', 'format-policy-01-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_01 = Record('format_response_01', 'format-response-01-rule', 'audit')
    # serialization formats
    FORMAT_JSON_02 = Record('format_json_02', 'format-json-02-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_02 = Record('format_audit_02', 'format-audit-02-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_02 = Record('format_identity_02', 'format-identity-02-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_02 = Record('format_lockout_02', 'format-lockout-02-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_02 = Record('format_policy_02', 'format-policy-02-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_02 = Record('format_response_02', 'format-response-02-rule', 'audit')
    # serialization formats
    FORMAT_JSON_03 = Record('format_json_03', 'format-json-03-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_03 = Record('format_audit_03', 'format-audit-03-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_03 = Record('format_identity_03', 'format-identity-03-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_03 = Record('format_lockout_03', 'format-lockout-03-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_03 = Record('format_policy_03', 'format-policy-03-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_03 = Record('format_response_03', 'format-response-03-rule', 'audit')
    # serialization formats
    FORMAT_JSON_04 = Record('format_json_04', 'format-json-04-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_04 = Record('format_audit_04', 'format-audit-04-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_04 = Record('format_identity_04', 'format-identity-04-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_04 = Record('format_lockout_04', 'format-lockout-04-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_04 = Record('format_policy_04', 'format-policy-04-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_04 = Record('format_response_04', 'format-response-04-rule', 'audit')
    # serialization formats
    FORMAT_JSON_05 = Record('format_json_05', 'format-json-05-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_05 = Record('format_audit_05', 'format-audit-05-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_05 = Record('format_identity_05', 'format-identity-05-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_05 = Record('format_lockout_05', 'format-lockout-05-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_05 = Record('format_policy_05', 'format-policy-05-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_05 = Record('format_response_05', 'format-response-05-rule', 'audit')
    # serialization formats
    FORMAT_JSON_06 = Record('format_json_06', 'format-json-06-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_06 = Record('format_audit_06', 'format-audit-06-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_06 = Record('format_identity_06', 'format-identity-06-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_06 = Record('format_lockout_06', 'format-lockout-06-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_06 = Record('format_policy_06', 'format-policy-06-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_06 = Record('format_response_06', 'format-response-06-rule', 'audit')
    # serialization formats
    FORMAT_JSON_07 = Record('format_json_07', 'format-json-07-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_07 = Record('format_audit_07', 'format-audit-07-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_07 = Record('format_identity_07', 'format-identity-07-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_07 = Record('format_lockout_07', 'format-lockout-07-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_07 = Record('format_policy_07', 'format-policy-07-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_07 = Record('format_response_07', 'format-response-07-rule', 'audit')
    # serialization formats
    FORMAT_JSON_08 = Record('format_json_08', 'format-json-08-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_08 = Record('format_audit_08', 'format-audit-08-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_08 = Record('format_identity_08', 'format-identity-08-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_08 = Record('format_lockout_08', 'format-lockout-08-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_08 = Record('format_policy_08', 'format-policy-08-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_08 = Record('format_response_08', 'format-response-08-rule', 'audit')
    # serialization formats
    FORMAT_JSON_09 = Record('format_json_09', 'format-json-09-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_09 = Record('format_audit_09', 'format-audit-09-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_09 = Record('format_identity_09', 'format-identity-09-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_09 = Record('format_lockout_09', 'format-lockout-09-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_09 = Record('format_policy_09', 'format-policy-09-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_09 = Record('format_response_09', 'format-response-09-rule', 'audit')
    # serialization formats
    FORMAT_JSON_10 = Record('format_json_10', 'format-json-10-rule', 'tenant')
    # serialization formats
    FORMAT_AUDIT_10 = Record('format_audit_10', 'format-audit-10-rule', 'request')
    # serialization formats
    FORMAT_IDENTITY_10 = Record('format_identity_10', 'format-identity-10-rule', 'audit')
    # serialization formats
    FORMAT_LOCKOUT_10 = Record('format_lockout_10', 'format-lockout-10-rule', 'tenant')
    # serialization formats
    FORMAT_POLICY_10 = Record('format_policy_10', 'format-policy-10-rule', 'request')
    # serialization formats
    FORMAT_RESPONSE_10 = Record('format_response_10', 'format-response-10-rule', 'audit')


def all_records():
    return (
        FORMAT_JSON_01,
        FORMAT_AUDIT_01,
        FORMAT_IDENTITY_01,
        FORMAT_LOCKOUT_01,
        FORMAT_POLICY_01,
        FORMAT_RESPONSE_01,
        FORMAT_JSON_02,
        FORMAT_AUDIT_02,
        FORMAT_IDENTITY_02,
        FORMAT_LOCKOUT_02,
        FORMAT_POLICY_02,
        FORMAT_RESPONSE_02,
        FORMAT_JSON_03,
        FORMAT_AUDIT_03,
        FORMAT_IDENTITY_03,
        FORMAT_LOCKOUT_03,
        FORMAT_POLICY_03,
        FORMAT_RESPONSE_03,
        FORMAT_JSON_04,
        FORMAT_AUDIT_04,
        FORMAT_IDENTITY_04,
        FORMAT_LOCKOUT_04,
        FORMAT_POLICY_04,
        FORMAT_RESPONSE_04,
        FORMAT_JSON_05,
        FORMAT_AUDIT_05,
        FORMAT_IDENTITY_05,
        FORMAT_LOCKOUT_05,
        FORMAT_POLICY_05,
        FORMAT_RESPONSE_05,
        FORMAT_JSON_06,
        FORMAT_AUDIT_06,
        FORMAT_IDENTITY_06,
        FORMAT_LOCKOUT_06,
        FORMAT_POLICY_06,
        FORMAT_RESPONSE_06,
        FORMAT_JSON_07,
        FORMAT_AUDIT_07,
        FORMAT_IDENTITY_07,
        FORMAT_LOCKOUT_07,
        FORMAT_POLICY_07,
        FORMAT_RESPONSE_07,
        FORMAT_JSON_08,
        FORMAT_AUDIT_08,
        FORMAT_IDENTITY_08,
        FORMAT_LOCKOUT_08,
        FORMAT_POLICY_08,
        FORMAT_RESPONSE_08,
        FORMAT_JSON_09,
        FORMAT_AUDIT_09,
        FORMAT_IDENTITY_09,
        FORMAT_LOCKOUT_09,
        FORMAT_POLICY_09,
        FORMAT_RESPONSE_09,
        FORMAT_JSON_10,
        FORMAT_AUDIT_10,
        FORMAT_IDENTITY_10,
        FORMAT_LOCKOUT_10,
        FORMAT_POLICY_10,
        FORMAT_RESPONSE_10,
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

