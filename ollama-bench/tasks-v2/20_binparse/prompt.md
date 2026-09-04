Create `container.py` in the current directory with two functions:

- `parse(data: bytes) -> dict`
- `pack(obj: dict) -> bytes`

They implement a small binary container format called BINP. Standard library only.

## Byte layout

A container is a byte string with this structure (all multi-byte integers are
**big-endian unsigned**):

1. Bytes 0..3: magic, exactly the ASCII bytes `BINP` (hex `42 49 4e 50`).
2. Byte 4: format version, a single unsigned byte. The only supported version is `2`.
3. Bytes 5..8: record count, a 4-byte (32-bit) big-endian unsigned integer.
4. Then the record area: exactly that many records, back to back, each encoded as
   described below.
5. Last 4 bytes of the container: a checksum (see below).

### Record encoding

Each record is:

1. A 1-byte flags field. Bit 0 (value `1`) set means the record has an optional
   field `score`; bit 1 (value `2`) set means it has an optional field `tag`.
   Bits 2..7 are reserved: in well-formed input they are `0`, and `parse` must
   ignore them (not raise). `pack` always writes them as `0`.
2. A 4-byte big-endian unsigned integer, field `id`.
3. A length-prefixed UTF-8 string, field `name`: a 4-byte big-endian unsigned
   length L, followed by exactly L bytes which decode as UTF-8 to `str`.
   The empty string (L = 0) is allowed.
4. If bit 0 of the flags byte is set: a 4-byte big-endian unsigned integer,
   field `score`.
5. If bit 1 of the flags byte is set: a length-prefixed UTF-8 string, field
   `tag`, encoded exactly like `name` (4-byte length, then that many bytes).

### Checksum

The final 4 bytes of the container hold `zlib.crc32` of **all preceding bytes of
the container** (offset 0 through the end of the record area, i.e. every byte
except the checksum itself), stored as a 4-byte big-endian unsigned integer
(`zlib.crc32(...)` already returns an unsigned int in Python 3).

### Parsed representation

`parse(data)` returns a dict `{"version": 2, "records": [...]}` where each
record is a dict with key `"id"` (`int`) and `"name"` (`str`) always present,
key `"score"` (`int`) present if and only if flag bit 0 was set, and key
`"tag"` (`str`) present if and only if flag bit 1 was set.

`pack(obj)` performs the inverse: it takes `{"version": 2, "records": [...]}`
with records as above (a record has optional field `score`/`tag` exactly when
that key is present in its dict), and returns the container bytes. Strings are
encoded as UTF-8. **For every well-formed byte string `d`,
`pack(parse(d)) == d` must hold.** The behaviour of `pack` on malformed input
objects is unspecified; the grader only calls `pack` on well-formed objects.

## Errors

Define a single exception base class in `container.py`:

    class ContainerError(Exception)

Every error below must be raised as an instance of the named subclass of
`ContainerError` (all seven classes must be defined in `container.py` and
subclass `ContainerError`, which itself subclasses `Exception`):

| Condition                                                                    | Exception class            |
|------------------------------------------------------------------------------|----------------------------|
| `len(data) < 13` (too short for magic + version + count + checksum)          | `TruncatedError`           |
| Magic bytes are not `BINP`                                                   | `BadMagicError`            |
| Version byte is not `2`                                                      | `UnsupportedVersionError`  |
| Stored checksum does not equal `zlib.crc32` of all preceding bytes           | `ChecksumError`            |
| The record area ends before all fixed-size fields needed next (a flags byte, an `id`, a `score`, or a string's 4-byte length) can be read | `TruncatedError` |
| A declared string length is greater than the number of bytes between the current read position and the start of the 4-byte checksum | `LengthError` |
| A string's payload bytes do not decode as UTF-8                              | `InvalidUTF8Error`         |
| After successfully reading the declared number of records, bytes remain before the checksum | `TrailingDataError` |

`parse` must perform its checks in this exact order, so exactly one of these
errors is raised when several conditions apply:

1. length < 13 → `TruncatedError`
2. magic → `BadMagicError`
3. version → `UnsupportedVersionError`
4. checksum (over `data[:-4]`, compared with the last 4 bytes big-endian) → `ChecksumError`
5. then parse the record area, raising `TruncatedError`, `LengthError` or
   `InvalidUTF8Error` as specified (for each string: check the length first,
   then decode UTF-8)
6. finally, if the record area did not end exactly at the checksum → `TrailingDataError`

Note: after the last record there must be **no** bytes left before the checksum;
a container whose record area stops short of the checksum raises
`TrailingDataError`, one whose record area would run into or past the checksum
raises `TruncatedError` or `LengthError` as specified above.

## Worked example

`pack({"version": 2, "records": [{"id": 1, "name": "ab", "score": 5}]})`
returns exactly this hex (spaces added for readability only):

    42 49 4e 50 02 00 00 00 01 01 00 00 00 01 00 00 00 02 61 62 00 00 00 05 a7 a3 b2 43

(the final 4 bytes are the CRC32 checksum of the preceding 24 bytes).
With no records: `pack({"version": 2, "records": []})` is
`42 49 4e 50 02 00 00 00 00 42 c5 b3 5a`.

Write a few quick checks of your own and run them with `python`, then reply "done".
