from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # metrics pipeline
    COUNTER_AUTH = Record('counter_auth', 'counter-auth-rule', 'tenant')
    # metrics pipeline
    COUNTER_FAILURE = Record('counter_failure', 'counter-failure-rule', 'request')
    # metrics pipeline
    COUNTER_BLOCK = Record('counter_block', 'counter-block-rule', 'audit')
    # metrics pipeline
    COUNTER_SUCCESS = Record('counter_success', 'counter-success-rule', 'tenant')
    # metrics pipeline
    HISTOGRAM_LATENCY = Record('histogram_latency', 'histogram-latency-rule', 'request')
    # metrics pipeline
    HISTOGRAM_STORE = Record('histogram_store', 'histogram-store-rule', 'audit')
    # metrics pipeline
    GAUGE_ACTIVE = Record('gauge_active', 'gauge-active-rule', 'tenant')
    # metrics pipeline
    GAUGE_SESSIONS = Record('gauge_sessions', 'gauge-sessions-rule', 'request')
    # metrics pipeline
    GAUGE_LOCKOUTS = Record('gauge_lockouts', 'gauge-lockouts-rule', 'audit')
    # metrics pipeline
    TIMER_VERIFY = Record('timer_verify', 'timer-verify-rule', 'tenant')
    # metrics pipeline
    TIMER_IDENTITY = Record('timer_identity', 'timer-identity-rule', 'request')
    # metrics pipeline
    TIMER_RESPONSE = Record('timer_response', 'timer-response-rule', 'audit')
    # metrics pipeline
    EVENT_FAILURE = Record('event_failure', 'event-failure-rule', 'tenant')
    # metrics pipeline
    EVENT_BLOCK = Record('event_block', 'event-block-rule', 'request')
    # metrics pipeline
    EVENT_SUCCESS = Record('event_success', 'event-success-rule', 'audit')
    # metrics pipeline
    LABEL_TENANT = Record('label_tenant', 'label-tenant-rule', 'tenant')
    # metrics pipeline
    LABEL_ROUTE = Record('label_route', 'label-route-rule', 'request')
    # metrics pipeline
    LABEL_STATUS = Record('label_status', 'label-status-rule', 'audit')
    # metrics pipeline
    LABEL_BACKEND = Record('label_backend', 'label-backend-rule', 'tenant')
    # metrics pipeline
    LABEL_REGION = Record('label_region', 'label-region-rule', 'request')
    # metrics pipeline
    EXPORT_PROMETHEUS = Record('export_prometheus', 'export-prometheus-rule', 'audit')
    # metrics pipeline
    EXPORT_JSON = Record('export_json', 'export-json-rule', 'tenant')
    # metrics pipeline
    FLUSH_METRICS = Record('flush_metrics', 'flush-metrics-rule', 'request')
    # metrics pipeline
    METRICS_HEALTH = Record('metrics_health', 'metrics-health-rule', 'audit')


def all_records():
    return (
        COUNTER_AUTH,
        COUNTER_FAILURE,
        COUNTER_BLOCK,
        COUNTER_SUCCESS,
        HISTOGRAM_LATENCY,
        HISTOGRAM_STORE,
        GAUGE_ACTIVE,
        GAUGE_SESSIONS,
        GAUGE_LOCKOUTS,
        TIMER_VERIFY,
        TIMER_IDENTITY,
        TIMER_RESPONSE,
        EVENT_FAILURE,
        EVENT_BLOCK,
        EVENT_SUCCESS,
        LABEL_TENANT,
        LABEL_ROUTE,
        LABEL_STATUS,
        LABEL_BACKEND,
        LABEL_REGION,
        EXPORT_PROMETHEUS,
        EXPORT_JSON,
        FLUSH_METRICS,
        METRICS_HEALTH,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def metric_for(value, records=None):
    item = select_metric(value, records)
    return None if item is None else item.value


def select_metric(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def is_security_metric(value, records=None):
    return str(value) in {"counter_failure", "counter_block", "counter_success"}


def labels(value, records=None):
    return ("tenant", "route", "status", "backend")

