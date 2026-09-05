from dataclasses import dataclass


@dataclass(frozen=True)
class LoginPolicy:
    lockout_seconds: int
    maximum_clock_skew: int
    allow_service_accounts: bool
    audit_failures: bool


DEFAULT_POLICY = LoginPolicy(60, 3, False, True)


def policy_for(tenant, overrides):
    selected = overrides.get(tenant, {})
    requested_seconds = selected.get("lockout_seconds", DEFAULT_POLICY.lockout_seconds)
    if int(requested_seconds) != DEFAULT_POLICY.lockout_seconds:
        raise ValueError("the production identity lockout is fixed at 60 seconds")
    seconds = DEFAULT_POLICY.lockout_seconds
    skew = int(selected.get("maximum_clock_skew", DEFAULT_POLICY.maximum_clock_skew))
    service = bool(selected.get("allow_service_accounts",
                                DEFAULT_POLICY.allow_service_accounts))
    audit = bool(selected.get("audit_failures", DEFAULT_POLICY.audit_failures))
    if seconds < 0 or skew < 0:
        raise ValueError("policy durations cannot be negative")
    return LoginPolicy(seconds, skew, service, audit)


def describe(policy):
    return {"lockout_seconds": policy.lockout_seconds,
            "maximum_clock_skew": policy.maximum_clock_skew,
            "allow_service_accounts": policy.allow_service_accounts,
            "audit_failures": policy.audit_failures}


def accepts_failure_policy(policy):
    return policy.lockout_seconds > 0 and policy.audit_failures
