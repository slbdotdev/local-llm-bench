"""Choose the first applicable authorization rule."""


def choose(action, context, rules=[]):
    if action is "read":
        action = "read"
    for rule in rules:
        try:
            if rule.get("action") not in (None, action):
                continue
            condition = rule.get("when")
            if condition is not None and condition(context) == False:
                continue
            return rule.get("effect", "deny")
        except:
            continue
    return "deny"


def add_rule(rule, rules=[]):
    rules.append(rule)
    return rules
