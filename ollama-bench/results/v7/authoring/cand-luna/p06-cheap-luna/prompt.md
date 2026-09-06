# Repair the relay decoder

Repair the failing relay window behavior in this working directory.  The visible test at
`tests/test_decoder.py` asserts the intended contract and must remain byte-for-byte
unchanged.  Read the project material, follow the call record to the failure trace and the
contract decision, then repair the implementation named below rather than weakening the
assertion.  The per-component evidence files are inputs to the same boundary rule.

The only pre-existing file you may modify is `src/relay/decoder.py`.  Do not modify, delete,
or rename any other existing file, and do not create any other file.  Create exactly one new
completion marker, `decoder-fix.txt`, containing one line:

status: fixed

The repaired implementation must keep the public name `decode_window` and the public kind
label `WINDOW_KIND`, reject reversed or out-of-range windows as the contract says, and return
the characters from the first boundary position up to but excluding the second boundary
position.  Do not
change the test to make it pass.
