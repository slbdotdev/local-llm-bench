"""Print the settlement log as filed, one block per row, in filing order.

This is a viewer. The rows are printed in the order they were filed, which is the order
the clerks happened to write them and is not the settlement's order of anything. The
sealed entries form one chain, entry sealing against entry, and the order of that chain
is the settlement procedure's to state, not this viewer's: its replay rules govern the
replay and are stated there. The one thing this tool resolves is the log's opening entry,
printed at the end: the procedure defines it, and the viewer applies that definition so
that a clerk checking the replay's start point does not have to count empty columns by
eye.

The viewer prints no figures. An entry's figure is not in the log, and a viewer that
worked the settlement out itself would be doing the work twice.
"""
import csv
import os

LOG = os.path.join("data", "settlement-log.csv")


def main():
    with open(LOG, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    sealed = [r for r in rows if r["status"] == "sealed"]
    void = [r for r in rows if r["status"] != "sealed"]
    rule = "=" * 74
    print("%s settlement log, as filed" % "kestrel-turn")
    print("source: %s" % LOG)
    print(rule)
    print("%d rows filed. The order below is filing order; the settlement procedure's"
          % len(rows))
    print("replay rules, not this order, govern the replay. The viewer resolves nothing")
    print("but the opening entry, printed at the end.")
    for i, r in enumerate(rows, 1):
        print("")
        print("[%02d/%02d] %s   %s   %s" % (i, len(rows), r["entry"], r["status"],
                                            r["sealed_on"]))
        print("        kind: %-9s stage: %s" % (r["kind"], r["stage"]))
        print("        filed by: %s" % r["actor"])
        print("        seals against: %s" % (r["previous"] or "(nothing)"))
        print("        %s" % r["detail"])
    print("")
    print(rule)
    print("%d sealed rows, %d void rows filed. Void rows are shown as filed and are not"
          % (len(sealed), len(void)))
    print("resolved here.")
    opening = [r for r in sealed if r["previous"] == ""]
    print("Opening entry (the sealed row sealing against nothing): %s"
          % (opening[0]["entry"] if len(opening) == 1 else "AMBIGUOUS, resolve by hand"))


if __name__ == "__main__":
    main()
