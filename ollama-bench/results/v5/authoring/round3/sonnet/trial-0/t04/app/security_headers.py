from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # security headers
    HEADER_CACHE_01 = Record('header_cache_01', 'header-cache-01-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_01 = Record('header_transport_01', 'header-transport-01-rule', 'request')
    # security headers
    HEADER_FRAME_01 = Record('header_frame_01', 'header-frame-01-rule', 'audit')
    # security headers
    HEADER_CONTENT_01 = Record('header_content_01', 'header-content-01-rule', 'tenant')
    # security headers
    HEADER_REFERRER_01 = Record('header_referrer_01', 'header-referrer-01-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_01 = Record('header_permissions_01', 'header-permissions-01-rule', 'audit')
    # security headers
    HEADER_CACHE_02 = Record('header_cache_02', 'header-cache-02-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_02 = Record('header_transport_02', 'header-transport-02-rule', 'request')
    # security headers
    HEADER_FRAME_02 = Record('header_frame_02', 'header-frame-02-rule', 'audit')
    # security headers
    HEADER_CONTENT_02 = Record('header_content_02', 'header-content-02-rule', 'tenant')
    # security headers
    HEADER_REFERRER_02 = Record('header_referrer_02', 'header-referrer-02-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_02 = Record('header_permissions_02', 'header-permissions-02-rule', 'audit')
    # security headers
    HEADER_CACHE_03 = Record('header_cache_03', 'header-cache-03-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_03 = Record('header_transport_03', 'header-transport-03-rule', 'request')
    # security headers
    HEADER_FRAME_03 = Record('header_frame_03', 'header-frame-03-rule', 'audit')
    # security headers
    HEADER_CONTENT_03 = Record('header_content_03', 'header-content-03-rule', 'tenant')
    # security headers
    HEADER_REFERRER_03 = Record('header_referrer_03', 'header-referrer-03-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_03 = Record('header_permissions_03', 'header-permissions-03-rule', 'audit')
    # security headers
    HEADER_CACHE_04 = Record('header_cache_04', 'header-cache-04-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_04 = Record('header_transport_04', 'header-transport-04-rule', 'request')
    # security headers
    HEADER_FRAME_04 = Record('header_frame_04', 'header-frame-04-rule', 'audit')
    # security headers
    HEADER_CONTENT_04 = Record('header_content_04', 'header-content-04-rule', 'tenant')
    # security headers
    HEADER_REFERRER_04 = Record('header_referrer_04', 'header-referrer-04-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_04 = Record('header_permissions_04', 'header-permissions-04-rule', 'audit')
    # security headers
    HEADER_CACHE_05 = Record('header_cache_05', 'header-cache-05-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_05 = Record('header_transport_05', 'header-transport-05-rule', 'request')
    # security headers
    HEADER_FRAME_05 = Record('header_frame_05', 'header-frame-05-rule', 'audit')
    # security headers
    HEADER_CONTENT_05 = Record('header_content_05', 'header-content-05-rule', 'tenant')
    # security headers
    HEADER_REFERRER_05 = Record('header_referrer_05', 'header-referrer-05-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_05 = Record('header_permissions_05', 'header-permissions-05-rule', 'audit')
    # security headers
    HEADER_CACHE_06 = Record('header_cache_06', 'header-cache-06-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_06 = Record('header_transport_06', 'header-transport-06-rule', 'request')
    # security headers
    HEADER_FRAME_06 = Record('header_frame_06', 'header-frame-06-rule', 'audit')
    # security headers
    HEADER_CONTENT_06 = Record('header_content_06', 'header-content-06-rule', 'tenant')
    # security headers
    HEADER_REFERRER_06 = Record('header_referrer_06', 'header-referrer-06-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_06 = Record('header_permissions_06', 'header-permissions-06-rule', 'audit')
    # security headers
    HEADER_CACHE_07 = Record('header_cache_07', 'header-cache-07-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_07 = Record('header_transport_07', 'header-transport-07-rule', 'request')
    # security headers
    HEADER_FRAME_07 = Record('header_frame_07', 'header-frame-07-rule', 'audit')
    # security headers
    HEADER_CONTENT_07 = Record('header_content_07', 'header-content-07-rule', 'tenant')
    # security headers
    HEADER_REFERRER_07 = Record('header_referrer_07', 'header-referrer-07-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_07 = Record('header_permissions_07', 'header-permissions-07-rule', 'audit')
    # security headers
    HEADER_CACHE_08 = Record('header_cache_08', 'header-cache-08-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_08 = Record('header_transport_08', 'header-transport-08-rule', 'request')
    # security headers
    HEADER_FRAME_08 = Record('header_frame_08', 'header-frame-08-rule', 'audit')
    # security headers
    HEADER_CONTENT_08 = Record('header_content_08', 'header-content-08-rule', 'tenant')
    # security headers
    HEADER_REFERRER_08 = Record('header_referrer_08', 'header-referrer-08-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_08 = Record('header_permissions_08', 'header-permissions-08-rule', 'audit')
    # security headers
    HEADER_CACHE_09 = Record('header_cache_09', 'header-cache-09-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_09 = Record('header_transport_09', 'header-transport-09-rule', 'request')
    # security headers
    HEADER_FRAME_09 = Record('header_frame_09', 'header-frame-09-rule', 'audit')
    # security headers
    HEADER_CONTENT_09 = Record('header_content_09', 'header-content-09-rule', 'tenant')
    # security headers
    HEADER_REFERRER_09 = Record('header_referrer_09', 'header-referrer-09-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_09 = Record('header_permissions_09', 'header-permissions-09-rule', 'audit')
    # security headers
    HEADER_CACHE_10 = Record('header_cache_10', 'header-cache-10-rule', 'tenant')
    # security headers
    HEADER_TRANSPORT_10 = Record('header_transport_10', 'header-transport-10-rule', 'request')
    # security headers
    HEADER_FRAME_10 = Record('header_frame_10', 'header-frame-10-rule', 'audit')
    # security headers
    HEADER_CONTENT_10 = Record('header_content_10', 'header-content-10-rule', 'tenant')
    # security headers
    HEADER_REFERRER_10 = Record('header_referrer_10', 'header-referrer-10-rule', 'request')
    # security headers
    HEADER_PERMISSIONS_10 = Record('header_permissions_10', 'header-permissions-10-rule', 'audit')


def all_records():
    return (
        HEADER_CACHE_01,
        HEADER_TRANSPORT_01,
        HEADER_FRAME_01,
        HEADER_CONTENT_01,
        HEADER_REFERRER_01,
        HEADER_PERMISSIONS_01,
        HEADER_CACHE_02,
        HEADER_TRANSPORT_02,
        HEADER_FRAME_02,
        HEADER_CONTENT_02,
        HEADER_REFERRER_02,
        HEADER_PERMISSIONS_02,
        HEADER_CACHE_03,
        HEADER_TRANSPORT_03,
        HEADER_FRAME_03,
        HEADER_CONTENT_03,
        HEADER_REFERRER_03,
        HEADER_PERMISSIONS_03,
        HEADER_CACHE_04,
        HEADER_TRANSPORT_04,
        HEADER_FRAME_04,
        HEADER_CONTENT_04,
        HEADER_REFERRER_04,
        HEADER_PERMISSIONS_04,
        HEADER_CACHE_05,
        HEADER_TRANSPORT_05,
        HEADER_FRAME_05,
        HEADER_CONTENT_05,
        HEADER_REFERRER_05,
        HEADER_PERMISSIONS_05,
        HEADER_CACHE_06,
        HEADER_TRANSPORT_06,
        HEADER_FRAME_06,
        HEADER_CONTENT_06,
        HEADER_REFERRER_06,
        HEADER_PERMISSIONS_06,
        HEADER_CACHE_07,
        HEADER_TRANSPORT_07,
        HEADER_FRAME_07,
        HEADER_CONTENT_07,
        HEADER_REFERRER_07,
        HEADER_PERMISSIONS_07,
        HEADER_CACHE_08,
        HEADER_TRANSPORT_08,
        HEADER_FRAME_08,
        HEADER_CONTENT_08,
        HEADER_REFERRER_08,
        HEADER_PERMISSIONS_08,
        HEADER_CACHE_09,
        HEADER_TRANSPORT_09,
        HEADER_FRAME_09,
        HEADER_CONTENT_09,
        HEADER_REFERRER_09,
        HEADER_PERMISSIONS_09,
        HEADER_CACHE_10,
        HEADER_TRANSPORT_10,
        HEADER_FRAME_10,
        HEADER_CONTENT_10,
        HEADER_REFERRER_10,
        HEADER_PERMISSIONS_10,
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

