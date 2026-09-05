from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # input validation
    TENANT_REQUIRED = Record('tenant_required', 'tenant-required-rule', 'tenant')
    # input validation
    ACCOUNT_REQUIRED = Record('account_required', 'account-required-rule', 'request')
    # input validation
    SECRET_REQUIRED = Record('secret_required', 'secret-required-rule', 'audit')
    # input validation
    TENANT_LENGTH = Record('tenant_length', 'tenant-length-rule', 'tenant')
    # input validation
    ACCOUNT_LENGTH = Record('account_length', 'account-length-rule', 'request')
    # input validation
    SECRET_LENGTH = Record('secret_length', 'secret-length-rule', 'audit')
    # input validation
    TENANT_CHARSET = Record('tenant_charset', 'tenant-charset-rule', 'tenant')
    # input validation
    ACCOUNT_CHARSET = Record('account_charset', 'account-charset-rule', 'request')
    # input validation
    SECRET_CHARSET = Record('secret_charset', 'secret-charset-rule', 'audit')
    # input validation
    HEADER_LENGTH = Record('header_length', 'header-length-rule', 'tenant')
    # input validation
    BODY_LENGTH = Record('body_length', 'body-length-rule', 'request')
    # input validation
    ROUTE_METHOD = Record('route_method', 'route-method-rule', 'audit')
    # input validation
    ROUTE_PATH = Record('route_path', 'route-path-rule', 'tenant')
    # input validation
    REQUEST_ID = Record('request_id', 'request-id-rule', 'request')
    # input validation
    TRACE_PARENT = Record('trace_parent', 'trace-parent-rule', 'audit')
    # input validation
    LOCALE = Record('locale', 'locale-rule', 'tenant')
    # input validation
    CONTENT_TYPE = Record('content_type', 'content-type-rule', 'request')
    # input validation
    FORWARDED_ADDRESS = Record('forwarded_address', 'forwarded-address-rule', 'audit')
    # input validation
    USER_AGENT = Record('user_agent', 'user-agent-rule', 'tenant')
    # input validation
    JSON_SHAPE = Record('json_shape', 'json-shape-rule', 'request')
    # input validation
    SCHEMA_VERSION = Record('schema_version', 'schema-version-rule', 'audit')
    # input validation
    POLICY_SHAPE = Record('policy_shape', 'policy-shape-rule', 'tenant')
    # input validation
    ADAPTER_SHAPE = Record('adapter_shape', 'adapter-shape-rule', 'request')
    # input validation
    RESPONSE_SHAPE = Record('response_shape', 'response-shape-rule', 'audit')
    # input validation
    AUDIT_SHAPE = Record('audit_shape', 'audit-shape-rule', 'tenant')


def all_records():
    return (
        TENANT_REQUIRED,
        ACCOUNT_REQUIRED,
        SECRET_REQUIRED,
        TENANT_LENGTH,
        ACCOUNT_LENGTH,
        SECRET_LENGTH,
        TENANT_CHARSET,
        ACCOUNT_CHARSET,
        SECRET_CHARSET,
        HEADER_LENGTH,
        BODY_LENGTH,
        ROUTE_METHOD,
        ROUTE_PATH,
        REQUEST_ID,
        TRACE_PARENT,
        LOCALE,
        CONTENT_TYPE,
        FORWARDED_ADDRESS,
        USER_AGENT,
        JSON_SHAPE,
        SCHEMA_VERSION,
        POLICY_SHAPE,
        ADAPTER_SHAPE,
        RESPONSE_SHAPE,
        AUDIT_SHAPE,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def rule_for(value, records=None):
    item = select_rule(value, records)
    return None if item is None else item.value


def select_rule(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_identity_rule(value, records=None):
    return str(value) in {"tenant_required", "account_required", "tenant_charset", "account_charset"}


def is_security_boundary(value, records=None):
    return str(value) in {"secret_required", "secret_charset", "json_shape"}

