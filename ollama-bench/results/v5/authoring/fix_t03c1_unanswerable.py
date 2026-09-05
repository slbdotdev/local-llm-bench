"""t03/cand-1 asserts two values its own material does not contain. Make the task answerable.

Found 2026-09-05 by `check_derivable.py`, then confirmed independently by the Sonnet guard
arm, which reported: "No incident date appears anywhere in the record (verified via exhaustive
numeric/date-pattern search), so per the instruction not to infer facts not stated,
incident_date was set to 'not stated in the record' rather than fabricated." That is the guard
arm doing exactly its job -- plan-2026-09-05 section 2.2: a task Sonnet fails is under
suspicion of being broken, not hard, until a reading proves otherwise. The reading proves it.

Defect 1 -- `incident_date` is fabricated. The reference asserts "2031-04-17". The string
"2031-04-17" does not appear in the seed; neither does "2031"; neither does any ISO date, in
any format. The prompt says "Do not infer or calculate facts that are not stated there", so
there is no correct answer to give. Two Haiku trials and one Sonnet trial all answered that it
was not stated, and all three were scored as failures -- and because a non-string value trips
the checker's shape gate, each lost all eight subchecks, not one. The field is REMOVED.

Defect 2 -- `impact_scope` is a paraphrase of the material, and the material is the authority.
The record says "delayed telemetry writes AFFECTING 12.4% of eu-west-2 tenants" (line 101).
The reference demanded "delayed telemetry writes FOR 12.4% of eu-west-2 tenants" -- a wording
that appears nowhere. The accept list and the reference are corrected to the material's own
words. This matters more since the prompt now requires values copied verbatim: the reference
was asking for a paraphrase while the prompt forbade one.

Both are "missing information", which plan-2026-09-05 section 2.3 excludes from the difficulty
ladder outright. Neither is difficulty; both look exactly like it.

Usage:  python3 fix_t03c1_unanswerable.py <task-dir> [<task-dir> ...]
        where <task-dir> holds prompt.md, test.py and ref/answer.json
"""
import json, os, sys

WRONG = "delayed telemetry writes for 12.4% of eu-west-2 tenants"
RIGHT = "delayed telemetry writes affecting 12.4% of eu-west-2 tenants"
MARK = "seven fields"


def patch(task):
    prompt_p = os.path.join(task, "prompt.md")
    test_p = os.path.join(task, "test.py")
    ref_p = os.path.join(task, "ref", "answer.json")
    prompt = open(prompt_p, encoding="utf-8").read()
    if MARK in prompt:
        print(f"{task}: already patched")
        return 0

    # 1. prompt: eight fields -> seven, and drop incident_date from the field list
    prompt = prompt.replace("exactly these eight fields", "exactly these seven fields")
    prompt = prompt.replace("`incident_date` (string), `affected_region`",
                            "`affected_region`")
    prompt = prompt.replace("eight fields", "seven fields")
    open(prompt_p, "w", encoding="utf-8").write(prompt)

    # 2. checker: drop the field from the ordered list and from the accept table,
    #    and correct impact_scope to the material's own wording
    test = open(test_p, encoding="utf-8").read()
    test = test.replace('_ora_fields = ["incident_date", "affected_region"',
                        '_ora_fields = ["affected_region"')
    for line in list(test.splitlines()):
        if line.strip().startswith('"incident_date":'):
            test = test.replace(line + "\n", "")
    test = test.replace(WRONG, RIGHT)
    open(test_p, "w", encoding="utf-8").write(test)

    # 3. reference answer: same two changes
    ref = json.load(open(ref_p, encoding="utf-8"))
    ref.pop("incident_date", None)
    if ref.get("impact_scope") == WRONG:
        ref["impact_scope"] = RIGHT
    json.dump(ref, open(ref_p, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"{task}: patched -- incident_date removed, impact_scope corrected")
    return 1


if __name__ == "__main__":
    for t in sys.argv[1:]:
        patch(t)
