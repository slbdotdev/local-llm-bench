from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # request metadata
    REQUEST_ID = Record('request_id', 'request-id-rule', 'tenant')
    # request metadata
    REMOTE_ADDRESS = Record('remote_address', 'remote-address-rule', 'request')
    # request metadata
    FORWARDED_ADDRESS = Record('forwarded_address', 'forwarded-address-rule', 'audit')
    # request metadata
    USER_AGENT = Record('user_agent', 'user-agent-rule', 'tenant')
    # request metadata
    ROUTE_NAME = Record('route_name', 'route-name-rule', 'request')
    # request metadata
    RECEIVED_AT = Record('received_at', 'received-at-rule', 'audit')
    # request metadata
    TENANT_HEADER = Record('tenant_header', 'tenant-header-rule', 'tenant')
    # request metadata
    ACCOUNT_HEADER = Record('account_header', 'account-header-rule', 'request')
    # request metadata
    TRACE_PARENT = Record('trace_parent', 'trace-parent-rule', 'audit')
    # request metadata
    LOCALE = Record('locale', 'locale-rule', 'tenant')
    # request metadata
    CONTENT_TYPE = Record('content_type', 'content-type-rule', 'request')
    # request metadata
    BODY_LENGTH = Record('body_length', 'body-length-rule', 'audit')
    # request metadata
    RETRY_COUNT = Record('retry_count', 'retry-count-rule', 'tenant')
    # request metadata
    CLIENT_VERSION = Record('client_version', 'client-version-rule', 'request')
    # request metadata
    REGION = Record('region', 'region-rule', 'audit')
    # request metadata
    EDGE_POP = Record('edge_pop', 'edge-pop-rule', 'tenant')
    # request metadata
    TLS_VERSION = Record('tls_version', 'tls-version-rule', 'request')
    # request metadata
    METHOD = Record('method', 'method-rule', 'audit')
    # request metadata
    PATH = Record('path', 'path-rule', 'tenant')
    # request metadata
    SCHEME = Record('scheme', 'scheme-rule', 'request')
    # request metadata
    HOST = Record('host', 'host-rule', 'audit')
    # request metadata
    PORT = Record('port', 'port-rule', 'tenant')
    # request metadata
    CONNECTION_ID = Record('connection_id', 'connection-id-rule', 'request')
    # request metadata
    SESSION_HINT = Record('session_hint', 'session-hint-rule', 'audit')


def all_records():
    return (
        REQUEST_ID,
        REMOTE_ADDRESS,
        FORWARDED_ADDRESS,
        USER_AGENT,
        ROUTE_NAME,
        RECEIVED_AT,
        TENANT_HEADER,
        ACCOUNT_HEADER,
        TRACE_PARENT,
        LOCALE,
        CONTENT_TYPE,
        BODY_LENGTH,
        RETRY_COUNT,
        CLIENT_VERSION,
        REGION,
        EDGE_POP,
        TLS_VERSION,
        METHOD,
        PATH,
        SCHEME,
        HOST,
        PORT,
        CONNECTION_ID,
        SESSION_HINT,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def normalize(value, records=None):
    text = str(value).strip()
    return text[:256]


def is_safe_header(value, records=None):
    text = normalize(value)
    return all(ord(ch) >= 32 for ch in text)


def with_request_id(value, records=None):
    item = select_request(value, records)
    return None if item is None else item.value


def select_request(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)

