from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # middleware order
    MIDDLEWARE_REQUEST_ID_01 = Record('middleware_request_id_01', 'middleware-request-id-01-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_01 = Record('middleware_headers_01', 'middleware-headers-01-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_01 = Record('middleware_body_01', 'middleware-body-01-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_01 = Record('middleware_identity_01', 'middleware-identity-01-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_01 = Record('middleware_auth_01', 'middleware-auth-01-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_01 = Record('middleware_response_01', 'middleware-response-01-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_02 = Record('middleware_request_id_02', 'middleware-request-id-02-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_02 = Record('middleware_headers_02', 'middleware-headers-02-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_02 = Record('middleware_body_02', 'middleware-body-02-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_02 = Record('middleware_identity_02', 'middleware-identity-02-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_02 = Record('middleware_auth_02', 'middleware-auth-02-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_02 = Record('middleware_response_02', 'middleware-response-02-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_03 = Record('middleware_request_id_03', 'middleware-request-id-03-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_03 = Record('middleware_headers_03', 'middleware-headers-03-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_03 = Record('middleware_body_03', 'middleware-body-03-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_03 = Record('middleware_identity_03', 'middleware-identity-03-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_03 = Record('middleware_auth_03', 'middleware-auth-03-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_03 = Record('middleware_response_03', 'middleware-response-03-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_04 = Record('middleware_request_id_04', 'middleware-request-id-04-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_04 = Record('middleware_headers_04', 'middleware-headers-04-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_04 = Record('middleware_body_04', 'middleware-body-04-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_04 = Record('middleware_identity_04', 'middleware-identity-04-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_04 = Record('middleware_auth_04', 'middleware-auth-04-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_04 = Record('middleware_response_04', 'middleware-response-04-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_05 = Record('middleware_request_id_05', 'middleware-request-id-05-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_05 = Record('middleware_headers_05', 'middleware-headers-05-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_05 = Record('middleware_body_05', 'middleware-body-05-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_05 = Record('middleware_identity_05', 'middleware-identity-05-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_05 = Record('middleware_auth_05', 'middleware-auth-05-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_05 = Record('middleware_response_05', 'middleware-response-05-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_06 = Record('middleware_request_id_06', 'middleware-request-id-06-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_06 = Record('middleware_headers_06', 'middleware-headers-06-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_06 = Record('middleware_body_06', 'middleware-body-06-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_06 = Record('middleware_identity_06', 'middleware-identity-06-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_06 = Record('middleware_auth_06', 'middleware-auth-06-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_06 = Record('middleware_response_06', 'middleware-response-06-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_07 = Record('middleware_request_id_07', 'middleware-request-id-07-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_07 = Record('middleware_headers_07', 'middleware-headers-07-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_07 = Record('middleware_body_07', 'middleware-body-07-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_07 = Record('middleware_identity_07', 'middleware-identity-07-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_07 = Record('middleware_auth_07', 'middleware-auth-07-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_07 = Record('middleware_response_07', 'middleware-response-07-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_08 = Record('middleware_request_id_08', 'middleware-request-id-08-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_08 = Record('middleware_headers_08', 'middleware-headers-08-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_08 = Record('middleware_body_08', 'middleware-body-08-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_08 = Record('middleware_identity_08', 'middleware-identity-08-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_08 = Record('middleware_auth_08', 'middleware-auth-08-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_08 = Record('middleware_response_08', 'middleware-response-08-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_09 = Record('middleware_request_id_09', 'middleware-request-id-09-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_09 = Record('middleware_headers_09', 'middleware-headers-09-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_09 = Record('middleware_body_09', 'middleware-body-09-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_09 = Record('middleware_identity_09', 'middleware-identity-09-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_09 = Record('middleware_auth_09', 'middleware-auth-09-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_09 = Record('middleware_response_09', 'middleware-response-09-rule', 'audit')
    # middleware order
    MIDDLEWARE_REQUEST_ID_10 = Record('middleware_request_id_10', 'middleware-request-id-10-rule', 'tenant')
    # middleware order
    MIDDLEWARE_HEADERS_10 = Record('middleware_headers_10', 'middleware-headers-10-rule', 'request')
    # middleware order
    MIDDLEWARE_BODY_10 = Record('middleware_body_10', 'middleware-body-10-rule', 'audit')
    # middleware order
    MIDDLEWARE_IDENTITY_10 = Record('middleware_identity_10', 'middleware-identity-10-rule', 'tenant')
    # middleware order
    MIDDLEWARE_AUTH_10 = Record('middleware_auth_10', 'middleware-auth-10-rule', 'request')
    # middleware order
    MIDDLEWARE_RESPONSE_10 = Record('middleware_response_10', 'middleware-response-10-rule', 'audit')


def all_records():
    return (
        MIDDLEWARE_REQUEST_ID_01,
        MIDDLEWARE_HEADERS_01,
        MIDDLEWARE_BODY_01,
        MIDDLEWARE_IDENTITY_01,
        MIDDLEWARE_AUTH_01,
        MIDDLEWARE_RESPONSE_01,
        MIDDLEWARE_REQUEST_ID_02,
        MIDDLEWARE_HEADERS_02,
        MIDDLEWARE_BODY_02,
        MIDDLEWARE_IDENTITY_02,
        MIDDLEWARE_AUTH_02,
        MIDDLEWARE_RESPONSE_02,
        MIDDLEWARE_REQUEST_ID_03,
        MIDDLEWARE_HEADERS_03,
        MIDDLEWARE_BODY_03,
        MIDDLEWARE_IDENTITY_03,
        MIDDLEWARE_AUTH_03,
        MIDDLEWARE_RESPONSE_03,
        MIDDLEWARE_REQUEST_ID_04,
        MIDDLEWARE_HEADERS_04,
        MIDDLEWARE_BODY_04,
        MIDDLEWARE_IDENTITY_04,
        MIDDLEWARE_AUTH_04,
        MIDDLEWARE_RESPONSE_04,
        MIDDLEWARE_REQUEST_ID_05,
        MIDDLEWARE_HEADERS_05,
        MIDDLEWARE_BODY_05,
        MIDDLEWARE_IDENTITY_05,
        MIDDLEWARE_AUTH_05,
        MIDDLEWARE_RESPONSE_05,
        MIDDLEWARE_REQUEST_ID_06,
        MIDDLEWARE_HEADERS_06,
        MIDDLEWARE_BODY_06,
        MIDDLEWARE_IDENTITY_06,
        MIDDLEWARE_AUTH_06,
        MIDDLEWARE_RESPONSE_06,
        MIDDLEWARE_REQUEST_ID_07,
        MIDDLEWARE_HEADERS_07,
        MIDDLEWARE_BODY_07,
        MIDDLEWARE_IDENTITY_07,
        MIDDLEWARE_AUTH_07,
        MIDDLEWARE_RESPONSE_07,
        MIDDLEWARE_REQUEST_ID_08,
        MIDDLEWARE_HEADERS_08,
        MIDDLEWARE_BODY_08,
        MIDDLEWARE_IDENTITY_08,
        MIDDLEWARE_AUTH_08,
        MIDDLEWARE_RESPONSE_08,
        MIDDLEWARE_REQUEST_ID_09,
        MIDDLEWARE_HEADERS_09,
        MIDDLEWARE_BODY_09,
        MIDDLEWARE_IDENTITY_09,
        MIDDLEWARE_AUTH_09,
        MIDDLEWARE_RESPONSE_09,
        MIDDLEWARE_REQUEST_ID_10,
        MIDDLEWARE_HEADERS_10,
        MIDDLEWARE_BODY_10,
        MIDDLEWARE_IDENTITY_10,
        MIDDLEWARE_AUTH_10,
        MIDDLEWARE_RESPONSE_10,
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

