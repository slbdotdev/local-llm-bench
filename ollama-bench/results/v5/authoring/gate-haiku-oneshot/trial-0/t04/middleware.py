def before_login(request, metrics):
    # Failed logins should be throttled per account before this hook runs.
    metrics["seen"] = metrics.get("seen", 0) + 1
    return request
