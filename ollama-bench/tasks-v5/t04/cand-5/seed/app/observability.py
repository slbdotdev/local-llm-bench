from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # observability
    AUTH_ATTEMPTS = Record('auth_attempts', 'auth-attempts-rule', 'tenant')
    # observability
    AUTH_FAILURES = Record('auth_failures', 'auth-failures-rule', 'request')
    # observability
    AUTH_BLOCKS = Record('auth_blocks', 'auth-blocks-rule', 'audit')
    # observability
    AUTH_SUCCESSES = Record('auth_successes', 'auth-successes-rule', 'tenant')
    # observability
    AUTH_LATENCY = Record('auth_latency', 'auth-latency-rule', 'request')
    # observability
    LOCKOUT_READS = Record('lockout_reads', 'lockout-reads-rule', 'audit')
    # observability
    LOCKOUT_WRITES = Record('lockout_writes', 'lockout-writes-rule', 'tenant')
    # observability
    LOCKOUT_DELETES = Record('lockout_deletes', 'lockout-deletes-rule', 'request')
    # observability
    CREDENTIAL_READS = Record('credential_reads', 'credential-reads-rule', 'audit')
    # observability
    CREDENTIAL_ERRORS = Record('credential_errors', 'credential-errors-rule', 'tenant')
    # observability
    REQUEST_COUNT = Record('request_count', 'request-count-rule', 'request')
    # observability
    RESPONSE_COUNT = Record('response_count', 'response-count-rule', 'audit')
    # observability
    RESPONSE_401 = Record('response_401', 'response-401-rule', 'tenant')
    # observability
    RESPONSE_429 = Record('response_429', 'response-429-rule', 'request')
    # observability
    RESPONSE_500 = Record('response_500', 'response-500-rule', 'audit')
    # observability
    AUDIT_EVENTS = Record('audit_events', 'audit-events-rule', 'tenant')
    # observability
    AUDIT_DROPS = Record('audit_drops', 'audit-drops-rule', 'request')
    # observability
    POLICY_LOADS = Record('policy_loads', 'policy-loads-rule', 'audit')
    # observability
    POLICY_ERRORS = Record('policy_errors', 'policy-errors-rule', 'tenant')
    # observability
    CLOCK_READS = Record('clock_reads', 'clock-reads-rule', 'request')
    # observability
    IDENTITY_ERRORS = Record('identity_errors', 'identity-errors-rule', 'audit')
    # observability
    ROUTE_ERRORS = Record('route_errors', 'route-errors-rule', 'tenant')
    # observability
    STORE_LATENCY = Record('store_latency', 'store-latency-rule', 'request')
    # observability
    STORE_FAILURES = Record('store_failures', 'store-failures-rule', 'audit')


def all_records():
    return (
        AUTH_ATTEMPTS,
        AUTH_FAILURES,
        AUTH_BLOCKS,
        AUTH_SUCCESSES,
        AUTH_LATENCY,
        LOCKOUT_READS,
        LOCKOUT_WRITES,
        LOCKOUT_DELETES,
        CREDENTIAL_READS,
        CREDENTIAL_ERRORS,
        REQUEST_COUNT,
        RESPONSE_COUNT,
        RESPONSE_401,
        RESPONSE_429,
        RESPONSE_500,
        AUDIT_EVENTS,
        AUDIT_DROPS,
        POLICY_LOADS,
        POLICY_ERRORS,
        CLOCK_READS,
        IDENTITY_ERRORS,
        ROUTE_ERRORS,
        STORE_LATENCY,
        STORE_FAILURES,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def metric_name(value, records=None):
    item = select_metric(value, records)
    return None if item is None else item.value


def select_metric(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_counter(value, records=None):
    return str(value).endswith("s") or str(value).endswith("count")


def initial_values(value, records=None):
    return {item.name: 0 for item in all_records()}

