"""Write a fresh intake-journal fixture set for onboarding and load tests.

Writes one empty journal per manifest stage -- headers only -- into the directory named
by --out. The directory must not already exist and must be outside the checkout: this
tool never writes inside the working tree, and the release journals under data/intake/
are never regenerated in place. Run with no arguments it prints this usage and changes
nothing.
"""
import json
import os
import sys

USAGE = "usage: make_fixtures.py --out <dir that does not exist>"
HEADER = "date,event,records,note"


def main(argv):
    if "--out" not in argv:
        print(USAGE)
        return 2
    out = argv[argv.index("--out") + 1]
    if os.path.exists(out) or out in (".", ".."):
        print("refusing: %s exists or is not a fresh directory" % out)
        return 2
    with open(os.path.join("config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    os.makedirs(out)
    for st in man["stages"]:
        p = os.path.join(out, st["name"] + ".csv")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER + "\n")
    print("wrote %d empty journals to %s" % (len(man["stages"]), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
