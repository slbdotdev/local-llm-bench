from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    tenant: str
    account: str

    def key(self):
        return self.tenant + ":" + self.account


def canonical_identity(tenant, account):
    tenant_text = str(tenant).strip().casefold()
    account_text = str(account).strip().casefold()
    if not tenant_text or not account_text:
        raise ValueError("identity fields cannot be empty")
    return Identity(tenant_text, account_text)


def same_identity(left, right):
    return left.tenant == right.tenant and left.account == right.account


def display_identity(identity):
    return "%s/%s" % (identity.tenant, identity.account)


def parse_external(value):
    text = str(value)
    if "/" not in text:
        raise ValueError("external identity needs tenant/account")
    tenant, account = text.split("/", 1)
    return canonical_identity(tenant, account)
