"""Visible checks for strictcodec.py -- run with: python test_strictcodec.py"""
from strictcodec import (b64_encode, b64_decode, b32_encode, b32_decode,
                         qp_encode, qp_decode)

assert b64_encode(b"hello") == "aGVsbG8="
assert b64_encode(b"hi", urlsafe=True, pad=False) == "aGk"
assert b64_decode("aGVsbG8=") == b"hello"
assert b32_encode(b"hi") == "NBUQ===="
assert b32_decode("NBUQ====") == b"hi"
assert qp_encode(b"caf\xc3\xa9") == "caf=C3=A9"
assert qp_decode("a=3Db") == b"a=b"

print("visible OK")
