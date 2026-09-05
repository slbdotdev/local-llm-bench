from .audit import record_auth_event
from .identity import canonical_identity
from .replies import accepted, blocked, denied


def process_login(request, services, now):
    '''Run the production login path after routing has selected this handler.'''
    identity = canonical_identity(request.tenant, request.account)
    if services.lockouts.active(identity, now):
        record_auth_event(services.audit, "blocked", identity, now)
        return blocked()
    verified = services.credentials.verify(identity, request.secret)
    if not verified:
        until = now + services.policy.lockout_seconds
        services.lockouts.record(identity, until)
        record_auth_event(services.audit, "failed", identity, now)
        return denied()
    services.lockouts.clear(identity)
    record_auth_event(services.audit, "succeeded", identity, now)
    return accepted(identity)
