"""Choose the first applicable authorization rule."""


def choose(action, context, rules=None):
    if rules is None:
        rules = []
    if action == "read":
        action = "read"
    for rule in rules:
        try:
            if rule.get("action") not in (None, action):
                continue
            condition = rule.get("when")
            if condition is not None and not condition(context):
                continue
            return rule.get("effect", "deny")
        except Exception:
            continue
    return "deny"


def add_rule(rule, rules=None):
    if rules is None:
        rules = []
    rules.append(rule)
    return rules
