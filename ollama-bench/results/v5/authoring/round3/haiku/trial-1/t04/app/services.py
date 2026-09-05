from dataclasses import dataclass


@dataclass
class Services:
    identity: object
    credentials: object
    lockouts: object
    policy: object
    audit: object
    health: object


def build_services(container):
    return Services(container.identity, container.credentials, container.lockouts,
                    container.policy, container.audit, container.health)


def required(service_set):
    fields = ("identity", "credentials", "lockouts", "policy", "audit", "health")
    return all(getattr(service_set, name, None) is not None for name in fields)


def replace_policy(service_set, policy):
    return Services(service_set.identity, service_set.credentials, service_set.lockouts,
                    policy, service_set.audit, service_set.health)
