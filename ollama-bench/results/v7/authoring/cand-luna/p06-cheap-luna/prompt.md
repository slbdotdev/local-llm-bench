# Repair the relay decoder

Repair the failing relay window behavior in this working directory.  The visible test at
`tests/test_decoder.py` asserts the intended contract and must remain byte-for-byte
unchanged.  Read the project material, follow the call record to the failure trace and the
contract decision and implementation policy, then repair the implementation named below rather
than weakening the assertion.  Reconcile the linked evidence before editing.

The only pre-existing file you may modify is `src/relay/decoder.py`.  Do not modify, delete,
or rename any other existing file, and do not create any other file.  Create exactly one new
completion marker, `decoder-fix.txt`, containing one line:

status: fixed

Do not change the test to make it pass.  Preserve the implementation's public entry point and
public kind label while applying the behavior established by the linked project evidence.
