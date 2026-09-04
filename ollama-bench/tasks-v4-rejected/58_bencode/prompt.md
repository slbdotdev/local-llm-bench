Create `bencode.py` in the current directory. It implements a **strict canonical**
bencode binary codec (pure Python, standard library only, no filesystem or network
access) and must define exactly this API:

- `BencodeError` — an exception class you define, subclassing `Exception`. Every error
  below is reported by raising `BencodeError`. Every instance must carry two attributes:
  `.kind`, one of the exact lowercase strings named below, and `.offset`. **Never** raise
  a bare `ValueError`/`TypeError`/`KeyError`, and never fall back silently.
- `encode(obj)` — returns `bytes`.
- `decode(data)` — takes `bytes`, returns the decoded object.

Banned: you must not import `bencodepy`, `pickle`, `json` or `ast`, and you must not
use the builtins `eval` or `exec` anywhere in the module.

## The four value types

| Python value | canonical encoding |
|---|---|
| `int` n | `i` + the decimal digits of n (with a leading `-` when negative) + `e` |
| `bytes` s | the decimal length of s + `:` + the raw bytes of s |
| `list` | `l` + the encodings of the elements in order + `e` |
| `dict` | `d` + for each key, the key's encoding immediately followed by its value's encoding + `e` |

Canonical form is exact and there is exactly one encoding of any encodable object:

- Integers carry **no leading zeros** and **no `-0`**: `i0e` is the only encoding of zero,
  and the first digit of a multi-digit integer is never `0`. Integers must satisfy
  `-2**63 <= n <= 2**63 - 1`.
- Byte-string length prefixes carry **no leading zeros** (`0:` is the empty byte string,
  but `00:` and `01:a` are not canonical). A length must be `<= 2**31 - 1`.
- Dictionary keys are always byte strings, are written **sorted ascending by raw
  unsigned byte value** (compare byte by byte; if one key is a prefix of the other, the
  shorter one sorts first), and no key may appear twice.
- **Nesting depth** is limited: the top-level value has depth 1, and a value written
  directly inside a list or a dict has depth one greater than that container. A `list`
  or `dict` whose own depth would exceed **32** is rejected. (Only lists and dicts are
  depth-limited; an `int` or `bytes` at depth 33 is fine.)
- Nothing may follow the top-level value.

## `encode(obj)`

`encode` walks the object and produces the canonical bytes. Its errors have
`.offset` **`None`** (there is no input byte to point at). Each value is validated in
exactly this order:

1. If `type(value) is bool`, raise kind `bool`. (`True`/`False` are rejected even though
   `bool` is a subclass of `int`.)
2. If the value's type is not *exactly* `int`, `bytes`, `list` or `dict`, raise kind
   `type`. So `str`, `bytearray`, `memoryview`, `tuple`, `set`, `float`, `None` and any
   subclass of the four allowed types are all rejected with kind `type`.
3. If it is an `int` outside `-2**63 .. 2**63 - 1`, raise kind `range`.
4. If it is a `list` or `dict` whose depth exceeds 32, raise kind `depth`.
5. If it is a `dict`, **all of its keys are checked before any value is looked at**: in
   the dict's own iteration (insertion) order, the first key whose type is not exactly
   `bytes` raises kind `key_type`.
6. Then the children are processed: list elements left to right; dict values in
   **sorted key order** (so for a dict written `{b"b": <bad1>, b"a": <bad2>}` it is
   `<bad2>`'s error that is raised).

## `decode(data)`

If `type(data)` is not exactly `bytes`, raise kind `type` with `.offset` `0` (so `str`,
`bytearray` and `memoryview` inputs are rejected). Otherwise parse one value starting at
offset 0; if it does not end exactly at `len(data)`, raise kind `trailing` with `.offset`
equal to the index of the first leftover byte.

`.offset` is always an index into `data`. Whenever the parser needs a byte that is not
there, the error is kind `truncated` with `.offset` equal to `len(data)` — that is the
only offset `truncated` ever reports.

**Parsing one value at offset `i`:**

- If `i == len(data)`: kind `truncated`.
- If `data[i]` is `i` (0x69): an **integer**. Let `j` be the index of the first `e` at or
  after `i+1`; if there is none, kind `truncated`. The body is `data[i+1:j]`. Let `k` be
  `i+2` if the body starts with `-`, else `i+1` (so `k` is where the digits start). Then,
  in this order:
  1. if `k >= j` (no digits at all, as in `ie` and `i-e`), kind `syntax` at offset `k`;
  2. scanning `k .. j-1` left to right, the first byte that is not an ASCII digit raises
     kind `syntax` at that byte's offset;
  3. if there is more than one digit and the first one is `0`, kind `leading_zero` at
     offset `k`;
  4. if the body is exactly `-0`, kind `negative_zero` at offset `i+1`;
  5. if the value is outside `-2**63 .. 2**63 - 1`, kind `range` at offset `i`.

  The value ends at `j+1`.
- If `data[i]` is an ASCII digit: a **byte string**. Let `j` be the index of the first `:`
  at or after `i`; if there is none, kind `truncated`. Then, in this order:
  1. scanning `i .. j-1` left to right, the first byte that is not an ASCII digit raises
     kind `syntax` at that byte's offset;
  2. if `j - i > 1` and `data[i]` is `0`, kind `leading_zero` at offset `i`;
  3. if the length exceeds `2**31 - 1`, kind `range` at offset `i`;
  4. if fewer than that many bytes remain after the `:`, kind `truncated`.

  The result is the `length` raw bytes after the `:`, ending at `j + 1 + length`.
- If `data[i]` is `l` (0x6C): a **list**. If its depth exceeds 32, kind `depth` at offset
  `i`. Then repeatedly, from offset `p = i+1`: if `p == len(data)`, kind `truncated`; if
  `data[p]` is `e`, the list ends at `p+1`; otherwise parse an element at `p` and
  continue from where it ended.
- If `data[i]` is `d` (0x64): a **dict**. If its depth exceeds 32, kind `depth` at offset
  `i`. Then repeatedly, from offset `p = i+1`: if `p == len(data)`, kind `truncated`; if
  `data[p]` is `e`, the dict ends at `p+1`. Otherwise a key is expected at `p`:
  1. if `data[p]` is `i`, `l` or `d`, kind `key_type` at offset `p` (keys must be byte
     strings);
  2. if `data[p]` is not an ASCII digit, kind `syntax` at offset `p`;
  3. parse the byte-string key at `p`; if it equals the previous key of this dict, kind
     `duplicate_key` at offset `p`; if it sorts before the previous key (raw unsigned
     byte comparison), kind `key_order` at offset `p`;
  4. parse the value at the offset where the key ended. (If the key is the last thing in
     the input, that parse reports `truncated`; if an `e` sits there, as in `d1:ae`, the
     value parse sees a byte that starts no value and reports kind `syntax` at that
     offset.)
- Any other byte: kind `syntax` at offset `i`.

Decoded values use exactly the four Python types: `int`, `bytes`, `list`, `dict`; a
decoded byte string is `bytes` and never `str`. For every object `x` that `encode`
accepts, `decode(encode(x)) == x`, and for every `data` that `decode` accepts,
`encode(decode(data)) == data`.

Examples:

- `encode(42) == b"i42e"` and `encode(b"spam") == b"4:spam"`
- `encode([b"a", 3]) == b"l1:ai3ee"` and `encode({b"b": 1, b"a": 2}) == b"d1:ai2e1:bi1ee"`
- `decode(b"d3:cow3:moo4:spam4:eggse") == {b"cow": b"moo", b"spam": b"eggs"}`
- `decode(b"li0eli1eee") == [0, [1]]`
- `decode(b"0:") == b""` and `encode({}) == b"de"`

Write a few quick checks of your own and run them with `python`, then reply "done".
