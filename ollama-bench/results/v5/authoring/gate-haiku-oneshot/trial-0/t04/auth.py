def verify(password, stored):
    return password == stored


def note_failure(account, metrics):
    metrics["login_failures"] = metrics.get("login_failures", 0) + 1
    metrics["last_failed_account"] = account


def reset_after_success(account, metrics):
    metrics.pop(("login_failures", account), None)
