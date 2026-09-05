from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # credential catalog
    CREDENTIAL_PASSWORD_01 = Record('credential_password_01', 'credential-password-01-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_01 = Record('credential_token_01', 'credential-token-01-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_01 = Record('credential_certificate_01', 'credential-certificate-01-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_01 = Record('credential_webauthn_01', 'credential-webauthn-01-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_01 = Record('credential_disabled_01', 'credential-disabled-01-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_01 = Record('credential_rotated_01', 'credential-rotated-01-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_02 = Record('credential_password_02', 'credential-password-02-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_02 = Record('credential_token_02', 'credential-token-02-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_02 = Record('credential_certificate_02', 'credential-certificate-02-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_02 = Record('credential_webauthn_02', 'credential-webauthn-02-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_02 = Record('credential_disabled_02', 'credential-disabled-02-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_02 = Record('credential_rotated_02', 'credential-rotated-02-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_03 = Record('credential_password_03', 'credential-password-03-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_03 = Record('credential_token_03', 'credential-token-03-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_03 = Record('credential_certificate_03', 'credential-certificate-03-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_03 = Record('credential_webauthn_03', 'credential-webauthn-03-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_03 = Record('credential_disabled_03', 'credential-disabled-03-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_03 = Record('credential_rotated_03', 'credential-rotated-03-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_04 = Record('credential_password_04', 'credential-password-04-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_04 = Record('credential_token_04', 'credential-token-04-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_04 = Record('credential_certificate_04', 'credential-certificate-04-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_04 = Record('credential_webauthn_04', 'credential-webauthn-04-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_04 = Record('credential_disabled_04', 'credential-disabled-04-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_04 = Record('credential_rotated_04', 'credential-rotated-04-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_05 = Record('credential_password_05', 'credential-password-05-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_05 = Record('credential_token_05', 'credential-token-05-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_05 = Record('credential_certificate_05', 'credential-certificate-05-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_05 = Record('credential_webauthn_05', 'credential-webauthn-05-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_05 = Record('credential_disabled_05', 'credential-disabled-05-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_05 = Record('credential_rotated_05', 'credential-rotated-05-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_06 = Record('credential_password_06', 'credential-password-06-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_06 = Record('credential_token_06', 'credential-token-06-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_06 = Record('credential_certificate_06', 'credential-certificate-06-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_06 = Record('credential_webauthn_06', 'credential-webauthn-06-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_06 = Record('credential_disabled_06', 'credential-disabled-06-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_06 = Record('credential_rotated_06', 'credential-rotated-06-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_07 = Record('credential_password_07', 'credential-password-07-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_07 = Record('credential_token_07', 'credential-token-07-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_07 = Record('credential_certificate_07', 'credential-certificate-07-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_07 = Record('credential_webauthn_07', 'credential-webauthn-07-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_07 = Record('credential_disabled_07', 'credential-disabled-07-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_07 = Record('credential_rotated_07', 'credential-rotated-07-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_08 = Record('credential_password_08', 'credential-password-08-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_08 = Record('credential_token_08', 'credential-token-08-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_08 = Record('credential_certificate_08', 'credential-certificate-08-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_08 = Record('credential_webauthn_08', 'credential-webauthn-08-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_08 = Record('credential_disabled_08', 'credential-disabled-08-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_08 = Record('credential_rotated_08', 'credential-rotated-08-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_09 = Record('credential_password_09', 'credential-password-09-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_09 = Record('credential_token_09', 'credential-token-09-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_09 = Record('credential_certificate_09', 'credential-certificate-09-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_09 = Record('credential_webauthn_09', 'credential-webauthn-09-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_09 = Record('credential_disabled_09', 'credential-disabled-09-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_09 = Record('credential_rotated_09', 'credential-rotated-09-rule', 'audit')
    # credential catalog
    CREDENTIAL_PASSWORD_10 = Record('credential_password_10', 'credential-password-10-rule', 'tenant')
    # credential catalog
    CREDENTIAL_TOKEN_10 = Record('credential_token_10', 'credential-token-10-rule', 'request')
    # credential catalog
    CREDENTIAL_CERTIFICATE_10 = Record('credential_certificate_10', 'credential-certificate-10-rule', 'audit')
    # credential catalog
    CREDENTIAL_WEBAUTHN_10 = Record('credential_webauthn_10', 'credential-webauthn-10-rule', 'tenant')
    # credential catalog
    CREDENTIAL_DISABLED_10 = Record('credential_disabled_10', 'credential-disabled-10-rule', 'request')
    # credential catalog
    CREDENTIAL_ROTATED_10 = Record('credential_rotated_10', 'credential-rotated-10-rule', 'audit')


def all_records():
    return (
        CREDENTIAL_PASSWORD_01,
        CREDENTIAL_TOKEN_01,
        CREDENTIAL_CERTIFICATE_01,
        CREDENTIAL_WEBAUTHN_01,
        CREDENTIAL_DISABLED_01,
        CREDENTIAL_ROTATED_01,
        CREDENTIAL_PASSWORD_02,
        CREDENTIAL_TOKEN_02,
        CREDENTIAL_CERTIFICATE_02,
        CREDENTIAL_WEBAUTHN_02,
        CREDENTIAL_DISABLED_02,
        CREDENTIAL_ROTATED_02,
        CREDENTIAL_PASSWORD_03,
        CREDENTIAL_TOKEN_03,
        CREDENTIAL_CERTIFICATE_03,
        CREDENTIAL_WEBAUTHN_03,
        CREDENTIAL_DISABLED_03,
        CREDENTIAL_ROTATED_03,
        CREDENTIAL_PASSWORD_04,
        CREDENTIAL_TOKEN_04,
        CREDENTIAL_CERTIFICATE_04,
        CREDENTIAL_WEBAUTHN_04,
        CREDENTIAL_DISABLED_04,
        CREDENTIAL_ROTATED_04,
        CREDENTIAL_PASSWORD_05,
        CREDENTIAL_TOKEN_05,
        CREDENTIAL_CERTIFICATE_05,
        CREDENTIAL_WEBAUTHN_05,
        CREDENTIAL_DISABLED_05,
        CREDENTIAL_ROTATED_05,
        CREDENTIAL_PASSWORD_06,
        CREDENTIAL_TOKEN_06,
        CREDENTIAL_CERTIFICATE_06,
        CREDENTIAL_WEBAUTHN_06,
        CREDENTIAL_DISABLED_06,
        CREDENTIAL_ROTATED_06,
        CREDENTIAL_PASSWORD_07,
        CREDENTIAL_TOKEN_07,
        CREDENTIAL_CERTIFICATE_07,
        CREDENTIAL_WEBAUTHN_07,
        CREDENTIAL_DISABLED_07,
        CREDENTIAL_ROTATED_07,
        CREDENTIAL_PASSWORD_08,
        CREDENTIAL_TOKEN_08,
        CREDENTIAL_CERTIFICATE_08,
        CREDENTIAL_WEBAUTHN_08,
        CREDENTIAL_DISABLED_08,
        CREDENTIAL_ROTATED_08,
        CREDENTIAL_PASSWORD_09,
        CREDENTIAL_TOKEN_09,
        CREDENTIAL_CERTIFICATE_09,
        CREDENTIAL_WEBAUTHN_09,
        CREDENTIAL_DISABLED_09,
        CREDENTIAL_ROTATED_09,
        CREDENTIAL_PASSWORD_10,
        CREDENTIAL_TOKEN_10,
        CREDENTIAL_CERTIFICATE_10,
        CREDENTIAL_WEBAUTHN_10,
        CREDENTIAL_DISABLED_10,
        CREDENTIAL_ROTATED_10,
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

