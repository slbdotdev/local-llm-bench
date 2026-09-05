import hashlib
import hmac


class CredentialVerifier:
    def __init__(self, directory, hasher=hashlib.sha256):
        self.directory = directory
        self.hasher = hasher

    def verify(self, identity, supplied):
        record = self.directory.lookup(identity.key())
        if record is None or record.disabled:
            return False
        digest = self.hasher(str(supplied).encode("utf-8")).hexdigest()
        return hmac.compare_digest(digest, record.digest)

    def describe(self, identity):
        record = self.directory.lookup(identity.key())
        return None if record is None else {"algorithm": record.algorithm,
                                              "disabled": record.disabled}


def constant_time_equal(left, right):
    return hmac.compare_digest(str(left), str(right))


def validate_record(record):
    return bool(record.account and record.digest and record.algorithm)


def digest_for(secret, hasher=hashlib.sha256):
    return hasher(str(secret).encode("utf-8")).hexdigest()
