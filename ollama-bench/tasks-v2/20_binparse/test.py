"""Hidden grader for 20_binparse."""
import sys, random, zlib

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)


try:
    import container
    from container import (ContainerError, BadMagicError, UnsupportedVersionError,
                           TruncatedError, ChecksumError, LengthError,
                           InvalidUTF8Error, TrailingDataError)

    P, K = container.parse, container.pack

    # --- exception hierarchy -------------------------------------------------
    for cls in (BadMagicError, UnsupportedVersionError, TruncatedError,
                ChecksumError, LengthError, InvalidUTF8Error, TrailingDataError):
        check(f"{cls.__name__} subclasses ContainerError", issubclass(cls, ContainerError))
    check("ContainerError subclasses Exception", issubclass(ContainerError, Exception))
    bases = {cls.__bases__[0] for cls in (BadMagicError, UnsupportedVersionError,
            TruncatedError, ChecksumError, LengthError, InvalidUTF8Error, TrailingDataError)}
    check("error classes are proper subclasses of ContainerError",
          all(issubclass(b, ContainerError) for b in bases))

    # --- helpers -------------------------------------------------------------
    def be32(n):
        return n.to_bytes(4, "big")

    def ref_pack(obj):
        out = b"BINP" + bytes([obj["version"]]) + be32(len(obj["records"]))
        for r in obj["records"]:
            flags = (1 if "score" in r else 0) | (2 if "tag" in r else 0)
            out += bytes([flags]) + be32(r["id"])
            nb = r["name"].encode("utf-8")
            out += be32(len(nb)) + nb
            if "score" in r:
                out += be32(r["score"])
            if "tag" in r:
                tb = r["tag"].encode("utf-8")
                out += be32(len(tb)) + tb
        return out + zlib.crc32(out).to_bytes(4, "big")

    def fix_crc(body):
        return body + zlib.crc32(body).to_bytes(4, "big")

    def expect(name, fn, exc):
        try:
            fn()
            fails.append(f"{name}: no {exc.__name__}")
        except exc:
            pass
        except Exception as e:
            fails.append(f"{name}: raised {type(e).__name__} not {exc.__name__}")

    # --- golden byte tests ---------------------------------------------------
    golden1 = bytes.fromhex("42494e500200000001010000000100000002616200000005a7a3b243")
    obj1 = {"version": 2, "records": [{"id": 1, "name": "ab", "score": 5}]}
    check("golden pack 1", K(obj1) == golden1)
    check("golden parse 1", P(golden1) == obj1)
    check("golden roundtrip 1", K(P(golden1)) == golden1)

    golden2 = bytes.fromhex("42494e50020000000042c5b35a")
    obj2 = {"version": 2, "records": []}
    check("golden pack 2", K(obj2) == golden2)
    check("golden parse 2", P(golden2) == obj2)

    obj3 = {"version": 2, "records": [{"id": 4294967295, "name": "", "score": 0}]}
    check("golden roundtrip 3 (max id, empty name)", K(P(ref_pack(obj3))) == ref_pack(obj3))
    check("golden parse 3", P(ref_pack(obj3)) == obj3)

    obj4 = {"version": 2, "records": [
        {"id": 7, "name": "héllo", "score": 300, "tag": "τag"},
        {"id": 0, "name": "x"},
        {"id": 9, "name": "y", "tag": ""},
    ]}
    d4 = ref_pack(obj4)
    check("golden parse 4", P(d4) == obj4)
    check("golden pack 4", K(obj4) == d4)
    check("golden roundtrip 4", K(P(d4)) == d4)

    # --- error cases (hand-built, checksums recomputed) -----------------------
    body1 = b"BINP" + b"\x02" + be32(0)
    expect("short input", lambda: P(b"B"), TruncatedError)
    expect("12-byte input", lambda: P(body1[:8] + b"\x00\x00\x00\x00"), TruncatedError)
    expect("bad magic", lambda: P(fix_crc(b"XINP" + b"\x02" + be32(0))), BadMagicError)
    expect("bad magic short but 13 bytes", lambda: P(b"XINP" + b"\x02" + be32(0) + b"\x00" * 4), BadMagicError)
    expect("bad magic under 13 bytes", lambda: P(b"XINP" + b"\x02" + b"\x00"), TruncatedError)
    expect("version 3", lambda: P(fix_crc(b"BINP" + b"\x03" + be32(0))), UnsupportedVersionError)
    expect("version 0", lambda: P(fix_crc(b"BINP" + b"\x00" + be32(0))), UnsupportedVersionError)
    expect("checksum mismatch", lambda: P(b"BINP" + b"\x02" + be32(0) + b"\x00\x00\x00\x00"), ChecksumError)
    expect("checksum mismatch payload", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(0))[:-1] + b"\xff"), ChecksumError)

    # truncated: count=1 but no record bytes
    expect("count 1 no records", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1))), TruncatedError)
    # truncated: record header present but id cut off
    expect("record id cut off", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + b"\x00\x00")), TruncatedError)
    # truncated: name length cut off
    expect("name length cut off", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + b"\x00\x00")), TruncatedError)
    # truncated: score field cut off
    expect("score cut off", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x01" + be32(1) + be32(0) + b"\x00\x00")), TruncatedError)

    # LengthError: declared name length 0xFFFFFFFF
    expect("name length overruns", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + b"\xff\xff\xff\xff")), LengthError)
    # LengthError: length runs into the checksum region (2 bytes short of 4-byte payload)
    expect("name length hits checksum", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + be32(6) + b"abcd")), LengthError)
    # but a name whose payload ends exactly at the checksum, with count=1, is fine
    ok_exact = fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + be32(4) + b"abcd")
    try:
        r = P(ok_exact)
        check("exact-fit name parses", r == {"version": 2, "records": [{"id": 1, "name": "abcd"}]})
    except Exception as e:
        fails.append(f"exact-fit name raised {type(e).__name__}")

    # InvalidUTF8Error
    expect("invalid utf-8 name", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + be32(2) + b"\xff\xfe")), InvalidUTF8Error)
    expect("invalid utf-8 tag", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x02" + be32(1) + be32(0) + be32(1) + b"\x80")), InvalidUTF8Error)

    # TrailingDataError: an extra byte between the record area and the checksum
    expect("trailing byte", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x00" + be32(1) + be32(2) + b"hi" + b"\x00")), TrailingDataError)
    expect("trailing bytes zero records", lambda: P(fix_crc(b"BINP" + b"\x02" + be32(0) + b"\x00\x00")), TrailingDataError)

    # reserved flag bits ignored (bit 7 set, no optional fields)
    d_res = fix_crc(b"BINP" + b"\x02" + be32(1) + b"\x80" + be32(3) + be32(1) + b"z")
    try:
        r = P(d_res)
        check("reserved flags ignored", r == {"version": 2, "records": [{"id": 3, "name": "z"}]})
    except Exception as e:
        fails.append(f"reserved flags raised {type(e).__name__}")

    # error precedence: bad magic AND bad version AND bad checksum -> BadMagicError
    expect("precedence magic>version>checksum", lambda: P(b"XINP" + b"\x09" + be32(0) + b"\x00\x00\x00\x00"), BadMagicError)
    expect("precedence version>checksum", lambda: P(b"BINP" + b"\x09" + be32(0) + b"\x00\x00\x00\x00"), UnsupportedVersionError)
    # truncated header beats checksum error
    expect("precedence short>magic", lambda: P(b"X"), TruncatedError)

    # --- randomised differential test ----------------------------------------
    random.seed(20)
    alphabets = ["ab", "aé日𝄞", "xy z\t"]
    def rstr(maxlen):
        return "".join(random.choice(random.choice(alphabets))
                       for _ in range(random.randint(0, maxlen)))
    for i in range(400):
        nrec = random.randint(0, 4)
        obj = {"version": 2, "records": []}
        for _ in range(nrec):
            rec = {"id": random.randint(0, 2**32 - 1), "name": rstr(6)}
            if random.random() < 0.5:
                rec["score"] = random.randint(0, 2**32 - 1)
            if random.random() < 0.5:
                rec["tag"] = rstr(4)
            obj["records"].append(rec)
        d = ref_pack(obj)
        try:
            got = P(d)
            check(f"rand {i} parse mismatch", got == obj)
            check(f"rand {i} roundtrip mismatch", K(got) == d)
        except Exception as e:
            fails.append(f"rand {i} raised {type(e).__name__}: {e}")

    # pack must also accept objects handed to it directly (not only via parse)
    check("pack direct object", K({"version": 2, "records": [{"id": 5, "name": "q", "tag": "T"}]}) == ref_pack({"version": 2, "records": [{"id": 5, "name": "q", "tag": "T"}]}))

except Exception as e:
    import traceback
    fails.append(f"exception: {e!r} {traceback.format_exc()[-200:]}")

if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")
