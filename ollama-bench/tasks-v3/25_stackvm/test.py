import sys, subprocess, textwrap

TOTAL = 23
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = f"{name} raised {type(e).__name__}"
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc):
    try:
        fn()
    except exc:
        return
    except Exception as e:
        fails.append(f"{name}: wrong exception {type(e).__name__}")
        return
    fails.append(f"{name}: no {getattr(exc, '__name__', exc)}")


vm = None
try:
    import vm
except Exception as e:
    fails.append(f"import failed: {e!r}")

if vm is not None:
    check("VMError is an Exception subclass",
          lambda: isinstance(vm.VMError, type) and issubclass(vm.VMError, Exception))

    _run = getattr(vm, "run", None)
    if callable(_run):
        run = _run
    else:
        def run(*a, **k):
            raise AttributeError("vm.run is missing or not callable")

    VMError = getattr(vm, "VMError", None)
    if not (isinstance(VMError, type) and issubclass(VMError, BaseException)):
        class VMError(Exception):
            """placeholder so check_raises records failures instead of crashing"""

    p1 = "PUSH 3\nPUSH 4\nADD\nPRINT\nHALT\n"
    check("add and print", lambda: run(p1) == [7])

    p2 = """
    PUSH 3
    LABEL loop
    DUP
    PRINT
    PUSH 1
    SUB
    DUP
    JZ end
    JMP loop
    LABEL end
    HALT
    """
    check("countdown loop", lambda: run(textwrap.dedent(p2)) == [3, 2, 1])

    check("halt only returns empty", lambda: run("HALT") == [])

    p3 = "PUSH 10\nPUSH 3\nDIV\nPRINT\nPUSH -7\nPUSH 2\nDIV\nPRINT\nHALT\n"
    check("floor division incl negative", lambda: run(p3) == [3, -4])

    p4 = "PUSH 1\nPUSH 2\nSWAP\nSUB\nPRINT\nHALT\n"
    check("swap then sub", lambda: run(p4) == [1])

    p5 = "PUSH 5\nDUP\nMUL\nPRINT\nHALT\n"
    check("dup then mul", lambda: run(p5) == [25])

    p6 = "PUSH 1\nPOP\nPUSH 9\nPRINT\nHALT\n"
    check("pop discards", lambda: run(p6) == [9])

    p7 = "# comment\n\nPUSH 2\n  PUSH 3  \nADD\nPRINT\nHALT\n"
    check("comments/blank lines/whitespace tolerated", lambda: run(p7) == [5])

    # error cases -> VMError
    bad_programs = {
        "unknown opcode": "PUSH 1\nFOO\nHALT\n",
        "push missing arg": "PUSH\nHALT\n",
        "push non-integer": "PUSH abc\nHALT\n",
        "add underflow": "PUSH 1\nADD\nHALT\n",
        "print underflow": "PRINT\nHALT\n",
        "dup underflow": "DUP\nHALT\n",
        "swap underflow": "PUSH 1\nSWAP\nHALT\n",
        "div by zero": "PUSH 1\nPUSH 0\nDIV\nHALT\n",
        "undefined label reached": "PUSH 1\nJMP nowhere\nHALT\n",
        "undefined label unreached": "PUSH 1\nJZ neverland\nHALT\n",
        "duplicate label": "LABEL x\nLABEL x\nHALT\n",
        "missing halt": "PUSH 1\nPRINT\n",
        "missing halt no ops": "PUSH 1\n",
    }
    for name_, prog in bad_programs.items():
        check_raises(f"error: {name_}", lambda p=prog: run(p), VMError)

    # infinite loop must not hang: run in a subprocess with a hard timeout
    loop_prog = "LABEL loop\nJMP loop\nHALT\n"
    script = (
        "import vm\n"
        "p = " + repr(loop_prog) + "\n"
        "try:\n"
        "    vm.run(p)\n"
        "    print('NOERROR')\n"
        "except vm.VMError:\n"
        "    print('VMERROR')\n"
        "except Exception as e:\n"
        "    print('OTHER', repr(e))\n"
    )

    def _loop_probe():
        try:
            r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            return False
        return "VMERROR" in r.stdout

    check("infinite loop raises VMError (not hang/crash)", _loop_probe)

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")
