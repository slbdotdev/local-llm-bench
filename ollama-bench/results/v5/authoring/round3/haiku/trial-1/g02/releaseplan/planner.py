"""Public orchestration for deterministic release plans."""
from .catalog import available, load_catalog
from .formatting import render
from .graph import order
from .history import canonical as canonical_name, load_history
from .lockfile import load_lock
from .policy import decision, load_policy


def plan_records(catalog_text, lock_text, policy_text, history_text,
                 target, platform, release):
    catalog = load_catalog(catalog_text)
    lock = load_lock(lock_text)
    policy = load_policy(policy_text)
    history = load_history(history_text)

    def canon(name):
        return canonical_name(name, release, history)

    target = canon(target)
    if target not in catalog or target not in lock:
        return []

    if not available(catalog[target], platform):
        return []

    def allowed(name):
        return (name in catalog and name in lock
                and decision(name, platform, release, policy) == "allow")

    try:
        return order(target, lock, catalog, canon, allowed)
    except KeyError:
        return []


def build_plan(catalog_text, lock_text, policy_text, history_text,
               target, platform, release):
    names = plan_records(catalog_text, lock_text, policy_text, history_text,
                         target, platform, release)
    if not names:
        return ""
    catalog = load_catalog(catalog_text)
    lock = load_lock(lock_text)
    target = canonical_name(target, release, load_history(history_text))
    return render(target, platform, release, names, catalog, lock)
