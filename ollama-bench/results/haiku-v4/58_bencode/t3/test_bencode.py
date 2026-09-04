"""Visible checks for bencode.py -- run with: python test_bencode.py"""
from bencode import encode, decode, BencodeError

assert encode(42) == b"i42e"
assert encode(b"spam") == b"4:spam"
assert encode([b"a", 3]) == b"l1:ai3ee"
assert encode({b"b": 1, b"a": 2}) == b"d1:ai2e1:bi1ee"
assert decode(b"d3:cow3:moo4:spam4:eggse") == {b"cow": b"moo", b"spam": b"eggs"}
assert decode(b"li0eli1eee") == [0, [1]]
assert decode(b"0:") == b""
assert encode({}) == b"de"
assert issubclass(BencodeError, Exception)

print("visible OK")
