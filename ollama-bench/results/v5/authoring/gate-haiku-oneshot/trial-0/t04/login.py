from auth import note_failure, verify


def login(account, password, stored, metrics):
    if verify(password, stored):
        return {"ok": True, "account": account}
    note_failure(account, metrics)
    return {"ok": False}
