from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # error taxonomy
    INVALID_REQUEST = Record('invalid_request', 'invalid-request-rule', 'tenant')
    # error taxonomy
    MISSING_IDENTITY = Record('missing_identity', 'missing-identity-rule', 'request')
    # error taxonomy
    UNKNOWN_IDENTITY = Record('unknown_identity', 'unknown-identity-rule', 'audit')
    # error taxonomy
    BAD_SECRET = Record('bad_secret', 'bad-secret-rule', 'tenant')
    # error taxonomy
    ACCOUNT_DISABLED = Record('account_disabled', 'account-disabled-rule', 'request')
    # error taxonomy
    LOCKED_IDENTITY = Record('locked_identity', 'locked-identity-rule', 'audit')
    # error taxonomy
    STORE_UNAVAILABLE = Record('store_unavailable', 'store-unavailable-rule', 'tenant')
    # error taxonomy
    STORE_CONFLICT = Record('store_conflict', 'store-conflict-rule', 'request')
    # error taxonomy
    POLICY_INVALID = Record('policy_invalid', 'policy-invalid-rule', 'audit')
    # error taxonomy
    CLOCK_INVALID = Record('clock_invalid', 'clock-invalid-rule', 'tenant')
    # error taxonomy
    AUDIT_UNAVAILABLE = Record('audit_unavailable', 'audit-unavailable-rule', 'request')
    # error taxonomy
    ROUTE_MISSING = Record('route_missing', 'route-missing-rule', 'audit')
    # error taxonomy
    METHOD_NOT_ALLOWED = Record('method_not_allowed', 'method-not-allowed-rule', 'tenant')
    # error taxonomy
    BODY_TOO_LARGE = Record('body_too_large', 'body-too-large-rule', 'request')
    # error taxonomy
    HEADER_INVALID = Record('header_invalid', 'header-invalid-rule', 'audit')
    # error taxonomy
    TENANT_MISSING = Record('tenant_missing', 'tenant-missing-rule', 'tenant')
    # error taxonomy
    ACCOUNT_MISSING = Record('account_missing', 'account-missing-rule', 'request')
    # error taxonomy
    SECRET_MISSING = Record('secret_missing', 'secret-missing-rule', 'audit')
    # error taxonomy
    TIMEOUT = Record('timeout', 'timeout-rule', 'tenant')
    # error taxonomy
    CANCELLED = Record('cancelled', 'cancelled-rule', 'request')
    # error taxonomy
    CONFIGURATION_MISSING = Record('configuration_missing', 'configuration-missing-rule', 'audit')
    # error taxonomy
    CONFIGURATION_INVALID = Record('configuration_invalid', 'configuration-invalid-rule', 'tenant')
    # error taxonomy
    MIGRATION_PENDING = Record('migration_pending', 'migration-pending-rule', 'request')
    # error taxonomy
    INTERNAL_ERROR = Record('internal_error', 'internal-error-rule', 'audit')


def all_records():
    return (
        INVALID_REQUEST,
        MISSING_IDENTITY,
        UNKNOWN_IDENTITY,
        BAD_SECRET,
        ACCOUNT_DISABLED,
        LOCKED_IDENTITY,
        STORE_UNAVAILABLE,
        STORE_CONFLICT,
        POLICY_INVALID,
        CLOCK_INVALID,
        AUDIT_UNAVAILABLE,
        ROUTE_MISSING,
        METHOD_NOT_ALLOWED,
        BODY_TOO_LARGE,
        HEADER_INVALID,
        TENANT_MISSING,
        ACCOUNT_MISSING,
        SECRET_MISSING,
        TIMEOUT,
        CANCELLED,
        CONFIGURATION_MISSING,
        CONFIGURATION_INVALID,
        MIGRATION_PENDING,
        INTERNAL_ERROR,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def error_for(value, records=None):
    item = select_error(value, records)
    return None if item is None else item.value


def select_error(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_auth_error(value, records=None):
    return str(value) in {"bad_secret", "account_disabled", "locked_identity"}


def public_status(value, records=None):
    return 429 if str(value) == "locked_identity" else 401 if str(value) in {"bad_secret", "unknown_identity"} else 400

