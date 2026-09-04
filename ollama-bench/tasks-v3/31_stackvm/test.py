import json
import subprocess
import sys

TOTAL = 44
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:12])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


WORKER = (
    "import json,sys\n"
    "import stackvm\n"
    "prog=json.loads(sys.argv[1])\n"
    "res={'ok':False,'out':None,'exc':'','msg':''}\n"
    "try:\n"
    "    res['out']=stackvm.run(prog)\n"
    "    res['ok']=True\n"
    "except Exception as e:\n"
    "    res['exc']=type(e).__name__\n"
    "    res['msg']=str(e)\n"
    "print(json.dumps(res))\n"
)


def vm(prog):
    try:
        r = subprocess.run(
            [sys.executable, "-c", WORKER, json.dumps(prog)],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return {"timeout": True}
    if r.returncode != 0:
        return {"crash": (r.stdout + r.stderr)[-300:]}
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return {"crash": r.stdout[-300:]}


def vm_out(prog):
    res = vm(prog)
    return res.get("out") if res.get("ok") else None


def vm_err(prog, exc_name, idx=None):
    res = vm(prog)
    if res.get("timeout") or res.get("crash") or res.get("ok"):
        return False
    if res.get("exc") != exc_name:
        return False
    if idx is not None and "at %d" % idx not in res.get("msg", ""):
        return False
    return True


try:
    import stackvm
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

EXC_NAMES = ["StackUnderflow", "UnknownOp", "BadOperand", "BadJump", "DuplicateLabel"]

# --- exception hierarchy (2) -------------------------------------------
check("exception classes exist",
      lambda: all(hasattr(stackvm, n) for n in ["VMError"] + EXC_NAMES))
check("hierarchy subclasses",
      lambda: issubclass(stackvm.VMError, Exception)
      and all(issubclass(getattr(stackvm, n), stackvm.VMError) for n in EXC_NAMES))

# --- basics (14) -------------------------------------------------------
check("empty program", lambda: vm_out([]) == [])
check("add", lambda: vm_out(["PUSH 2", "PUSH 3", "ADD", "PRINT"]) == ["5"])
check("sub order", lambda: vm_out(["PUSH 10", "PUSH 4", "SUB", "PRINT"]) == ["6"])
check("mul", lambda: vm_out(["PUSH 6", "PUSH 7", "MUL", "PRINT"]) == ["42"])
check("div trunc", lambda: vm_out(["PUSH 7", "PUSH 2", "DIV", "PRINT"]) == ["3"])
check("div neg", lambda: vm_out(["PUSH -7", "PUSH 2", "DIV", "PRINT"]) == ["-3"])
check("div neg divisor", lambda: vm_out(["PUSH 7", "PUSH -2", "DIV", "PRINT"]) == ["-3"])
check("div by zero",
      lambda: vm_err(["PUSH 5", "PUSH 0", "DIV", "PRINT"], "ZeroDivisionError"))
check("swap direction", lambda: vm_out(["PUSH 1", "PUSH 2", "SWAP", "PRINT"]) == ["1"])
check("dup", lambda: vm_out(["PUSH 1", "DUP", "MUL", "PRINT"]) == ["1"])
check("drop", lambda: vm_out(["PUSH 1", "PUSH 2", "DROP", "PRINT"]) == ["1"])
check("output order",
      lambda: vm_out(["PUSH 1", "PRINT", "PUSH 2", "PRINT"]) == ["1", "2"])
check("negative push", lambda: vm_out(["PUSH -3", "PRINT"]) == ["-3"])
check("big ints",
      lambda: vm_out(["PUSH 1000000000", "DUP", "MUL", "PRINT"])
      == ["1000000000000000000"])

# --- underflows (7) ----------------------------------------------------
check("underflow add", lambda: vm_err(["PUSH 1", "ADD"], "StackUnderflow"))
check("underflow dup", lambda: vm_err(["DUP"], "StackUnderflow"))
check("underflow swap", lambda: vm_err(["PUSH 1", "SWAP"], "StackUnderflow"))
check("underflow drop", lambda: vm_err(["DROP"], "StackUnderflow"))
check("underflow print", lambda: vm_err(["PRINT"], "StackUnderflow", idx=0))
check("underflow jz pops first", lambda: vm_err(["JZ nowhere"], "StackUnderflow"))
check("underflow index in msg",
      lambda: vm_err(["PUSH 1", "DROP", "DROP"], "StackUnderflow", idx=2))

# --- unknown ops and bad operands (12) ---------------------------------
check("unknown op lowercase", lambda: vm_err(["push 3"], "UnknownOp"))
check("unknown op empty", lambda: vm_err([""], "UnknownOp"))
check("unknown op whitespace", lambda: vm_err(["   "], "UnknownOp"))
# Arity errors are checked with enough values already on the stack, so that
# only the operand error is possible (never a stack underflow).
BAD_OPERAND = [
    ["PUSH"],
    ["PUSH x"],
    ["PUSH 1.5"],
    ["PUSH +3"],
    ["PUSH 1 2"],
    ["PUSH 1", "PUSH 1", "ADD 5"],
    ["PUSH 1", "DUP 1"],
    ["JMP"],
    ["LABEL"],
]
for prog in BAD_OPERAND:
    check("bad operand %r" % (prog,), lambda prog=prog: vm_err(prog, "BadOperand"))

# --- jumps and labels (9) ----------------------------------------------
check("jz not taken unknown label", lambda: vm_out(["PUSH 1", "JZ nowhere"]) == [])
check("jz taken forward",
      lambda: vm_out(["PUSH 0", "JZ end", "PRINT", "LABEL end"]) == [])
check("jmp skips print", lambda: vm_out(["JMP a", "PRINT", "LABEL a"]) == [])
check("jnz loop 1..5",
      lambda: vm_out(["PUSH 1", "LABEL loop", "DUP", "PRINT", "PUSH 1", "ADD",
                      "DUP", "PUSH 6", "SUB", "JNZ loop", "DROP"])
      == ["1", "2", "3", "4", "5"])
check("countdown",
      lambda: vm_out(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB",
                      "DUP", "JNZ top", "DROP"]) == ["3", "2", "1"])
check("bad jump jmp", lambda: vm_err(["PUSH 1", "JMP nowhere"], "BadJump", idx=1))
check("bad jump jz taken", lambda: vm_err(["PUSH 0", "JZ nowhere"], "BadJump"))
check("duplicate label",
      lambda: vm_err(["LABEL a", "PUSH 1", "LABEL a"], "DuplicateLabel", idx=0))
check("label checks lazy",
      lambda: vm_err(["PRINT", "LABEL a", "LABEL a"], "StackUnderflow", idx=0))

report()
