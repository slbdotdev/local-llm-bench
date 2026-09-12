"""Shared machinery for v8 item 2 (near-window in-prompt occupancy) and item 4 (abstention).

Nothing in here touches a GPU or a network. Every number this module produces is a
deterministic function of a seed and the text it generates.

Token counting is **pibench.py's own method and constant**, so the rung numbers are
comparable with v7's: `pibench.build_filled_prompt` sizes a prompt by
`target_chars = int(fill_tokens * FILL_CHARS_PER_TOKEN)` with
`FILL_CHARS_PER_TOKEN = 4.664` (measured against q27-Q3_K_S: 47,635 chars -> 10,213
prompt tokens). The inverse is used here: `tokens = round(chars / 4.664)`.

Evidence that the constant tracks the live harness, from v5's own records
(`results/accept-64k.json`): `fill_tokens_requested 57000`, `prompt_chars 265879`
(= 57,004 tokens at 4.664) came back as `achieved_fill_prompt_tokens 57871` at
`turns 1` -- an 867-token harness overhead (pi's system prompt plus tool schemas) on top
of the prompt itself. `results/calib-six.json` at 20,007 prompt tokens over 4-6 turns
came back 21,462-23,459, so the per-turn growth is ~300-700 tokens. Both figures are
recorded in every slot's MANIFEST.json as `harness_overhead_note`.
"""
import hashlib
import json
import os
import random
import re
import shutil
import tempfile

CHARS_PER_TOKEN = 4.664          # pibench.py FILL_CHARS_PER_TOKEN, unchanged
STRATA = (0.10, 0.30, 0.50, 0.70, 0.90)
ABSTAIN = "INSUFFICIENT"

# The one clause the A/B turns on. It appears in the `-abst` arm and nowhere in the
# `-noabst` arm, and the two prompt.md files differ in exactly these lines.
ABSTENTION_CLAUSE = """
If the material does not determine the answer to a question -- because the fact is not
recorded anywhere in it, or because the material leaves the question open -- answer that
question with the string `INSUFFICIENT` instead of supplying a value. Answering
`INSUFFICIENT` where the material does determine an answer is a failure of the same kind,
so use it only where the material genuinely does not decide.
"""


def count_tokens(text, cpt=CHARS_PER_TOKEN):
    """pibench's measure, inverted. Characters, not bytes: the prompt is delivered as text."""
    return int(round(len(text) / cpt))


def target_chars(tokens, cpt=CHARS_PER_TOKEN):
    return int(round(tokens * cpt))


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------
# Names. Every generated entity gets a textually unique name, which is what keeps the
# narrative lines unique: v7's most-repeated instrument defect was a value-bearing line
# sitting inside a byte-identical frame at a fixed offset across most units
# (decisions-r5, q09/q08). `frame_report()` below measures that this has not happened.
# --------------------------------------------------------------------------------------
ADJ = """amber auburn basalt beacon birch bramble brindle bronze calder cedar chalk cinder
clover copper coral crag dapple dusk ember fallow fennel flint garnet gorse granite harrow
hazel heather hollow indigo jasper kestrel lichen linden marram meadow mellow midland
nettle ochre osier pebble pewter quarry quince ridge rowan russet saffron sable sedge
shale sorrel spindle tamarisk teasel thistle umber vellum verdigris willow yarrow""".split()

NOUN = """anchorage bank barrow basin beck bight bluff bourne brae brook butte cairn
causeway channel cleave combe coomb copse cove crossing culvert dale delve dingle down
drift fell ferry ford furlong gate ghyll glade gully hallow haven headland hollow holt
knap knoll landing ledge mere mill moor narrows pasture pike pound quay reach rill
ripple sand scarp shaw shoal slade spur staithe strand tarn terrace thwaite vale
warren weir wharf withy yard""".split()


def unique_names(n, rng):
    pairs = [(a, b) for a in ADJ for b in NOUN]
    rng.shuffle(pairs)
    assert len(pairs) >= n, "name pool too small for %d entities" % n
    return ["%s %s" % (a.capitalize(), b.capitalize()) for a, b in pairs[:n]]


# --------------------------------------------------------------------------------------
# Narrative. Each template mentions the entity by name or id, so no rendered line is
# shared between two entities. `frame_report()` proves it rather than assuming it.
# --------------------------------------------------------------------------------------
NARRATIVE = [
    "The survey party reached {name} on the {ord1} of the month and found the access track passable for light vehicles only.",
    "Access to {name} is by the service road from the south; the gate code was reissued after the {ord1} inspection.",
    "{name} has been on the register since the first consolidation and its paperwork has never been reconstructed.",
    "Telemetry from {id} arrives on the {ord1} relay and is batched nightly rather than streamed.",
    "A housekeeping note against {id} asks that the cable run be rewalked before the next dry season.",
    "The logbook kept at {name} runs to {n1} pages and the earlier volumes are held off site.",
    "Weather at {name} closed the approach for {n2} days during the period under review and no readings were lost.",
    "The enclosure at {name} was rebuilt in timber after the old fencing was taken by the river.",
    "Correspondence about {id} is filed under the district rather than under the site, which has caused confusion before.",
    "{name} shares its power feed with the neighbouring pumping station and has its own cut-out.",
    "An earlier clerk recorded {name} under a shortened spelling, and both forms still appear in the older indexes.",
    "The instrument housing at {name} is the original pattern and its door seal is checked each visit.",
    "Maintenance visits to {id} are scheduled quarterly and the {ord1} of those was carried out as planned.",
    "The approach to {name} crosses {n2} field boundaries and the wayleave is held by the county.",
    "Signal strength at {name} has been marginal since the mast on the ridge was lowered.",
    "A spare sensor head is kept at {name} against the failure that took out the district in the previous cycle.",
    "The notes for {id} mention a disused well inside the compound, capped and recorded but not surveyed.",
    "Drainage work near {name} was completed without interruption to the record.",
    "The site plan for {name} is the {ord1} revision and supersedes the sketch held in the district folder.",
    "{id} was one of the sites brought forward in the consolidation and its numbering reflects that order.",
    "The fence line at {name} was rerun {n2} metres to the east to clear the culvert.",
    "A visitor log is kept at {name} and shows {n1} entries for the period.",
    "Calibration gear for {id} travels with the district van and is shared with {n2} other sites.",
    "The reading shelter at {name} takes water in heavy weather and the floor was relaid.",
    "Two of the anchors at {name} were replaced after the frost and the work is recorded in the district ledger.",
    "Correspondence shows the tenancy at {name} was renewed for a further {n1} years.",
    "The access key for {id} is held at the district office and signed out per visit.",
    "Vegetation around {name} is cut back twice a year under the standing arrangement.",
]

ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
            "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth"]


SOURCE_NARRATIVE = [
    "{id} was tabled by the platform group and circulated to {n2} reviewers before the board saw it.",
    "The discussion behind {id} ran over two sittings and is minuted under the title \"{name}\".",
    "{id} is filed in the {ord1} bundle and cross-referenced from the operations index.",
    "A dissent was lodged against {id} on procedural grounds and later withdrawn.",
    "The author of {id} has since moved teams and the document is maintained by the duty rota.",
    "{id}, \"{name}\", replaced a working note that was never given an identifier.",
    "The board asked for {n1} clarifications before accepting the text of {id}.",
    "{id} carries an appendix that reproduces the measurement method in full.",
    "Numbering for {id} follows the old scheme and was not renumbered at the consolidation.",
    "\"{name}\" is the title {id} is indexed under, which is not the title on its first page.",
    "{id} is the shortest document in the {ord1} bundle and has never been amended.",
    "A translation of {id} is held for the partner site and is informative only.",
    "{id} was drafted against the previous platform revision and re-checked afterwards.",
    "The review of {id} noted that {n2} of its cross-references point at retired documents.",
    "Comments on {id} are retained in the archive and are not part of the document.",
    "{id} is quoted in training material, which is not a source for any value.",
    "The {ord1} reading of {id} changed its wording but none of its figures.",
    "{id} is one of {n1} documents the index lists under the same heading.",
    "An editorial pass over {id} normalised its units without changing any figure.",
    "{id} is held in the register as \"{name}\" and is available to the duty engineer.",
    "The covering note to {id} asks that it be read with the platform overview.",
    "{id} was circulated late and the board minuted that fact without objecting to it.",
    "Two figures in {id} were transcribed from a spreadsheet that no longer exists.",
    "{id} has an erratum sheet correcting a spelling and nothing else.",
    "The file card for {id} records {n2} prior drafts, none of them retained.",
    "{id} is cited by the onboarding guide, which paraphrases it rather than quoting it.",
]


def narrative_lines(entity_id, name, k, rng, pool=None):
    """k narrative sentences for one entity, each textually unique to that entity."""
    pool = pool or NARRATIVE
    idx = list(range(len(pool)))
    rng.shuffle(idx)
    out = []
    for i in idx[:k]:
        out.append(pool[i].format(id=entity_id, name=name,
                                  ord1=rng.choice(ORDINALS),
                                  n1=rng.randint(3, 90), n2=rng.randint(2, 40)))
    return out


# --------------------------------------------------------------------------------------
# Convergence on a rung. A rung that cannot be hit within 15% is a void cell under the
# v8 plan section 4, so the generator converges rather than reporting a miss: the knob is
# the per-block narrative length, spread over unmarked blocks so no single block becomes
# an outlier, with the block count as the coarse knob.
# --------------------------------------------------------------------------------------
def tune_narrative(blocks, render, want_chars, rng, min_narr=1, max_narr=13, tol=0.0015,
                   max_rounds=400):
    """Adjust `blocks[i]["narr"]` until len(render()) is within `tol` of `want_chars`.

    `blocks` is a list of dicts each carrying an int `narr` and a bool `locked`.
    Only unlocked blocks are adjusted. Returns (realised_chars, rounds_used).
    """
    order = [i for i, b in enumerate(blocks) if not b.get("locked")]
    assert order, "no adjustable blocks"
    rng.shuffle(order)
    cursor = 0
    for rounds in range(max_rounds):
        text = render()
        have = len(text)
        if abs(have - want_chars) <= tol * want_chars:
            return have, rounds
        # one sentence is worth roughly this much; step by a whole number of sentences
        per = 120.0
        need = int(round((want_chars - have) / per))
        if need == 0:
            need = 1 if have < want_chars else -1
        step = 1 if need > 0 else -1
        moved = 0
        guard = 0
        while moved < abs(need) and guard < 4 * len(order) + 8:
            i = order[cursor % len(order)]
            cursor += 1
            guard += 1
            n = blocks[i]["narr"] + step
            if min_narr <= n <= max_narr:
                blocks[i]["narr"] = n
                moved += 1
        if moved == 0:
            return len(render()), rounds       # range exhausted; caller widens block count
    return len(render()), max_rounds


def frame_report(text, min_len=26):
    """How often the most-repeated substantive line recurs, and how many recur at all.

    v7's decisions-r5 closes with: "the frame measure should be run over every token in
    seed/, not only over the giveaway vocabulary, and a candidate whose value-bearing
    lines share a byte-identical frame at a fixed line offset across most units should
    fail whether or not the prompt names it". This runs over every line of the prompt.
    """
    counts = {}
    for line in text.splitlines():
        s = line.strip()
        if len(s) < min_len or s.startswith("#") or s.startswith("|"):
            continue
        counts[s] = counts.get(s, 0) + 1
    repeated = {k: v for k, v in counts.items() if v > 1}
    worst = max(repeated.values()) if repeated else 1
    examples = sorted(repeated.items(), key=lambda kv: -kv[1])[:3]
    return {"substantive_lines": len(counts), "lines_repeated": len(repeated),
            "max_line_repeats": worst,
            "worst_examples": [{"count": v, "line": k[:90]} for k, v in examples]}


# --------------------------------------------------------------------------------------
# Slot writing
# --------------------------------------------------------------------------------------
SLOT_NOTICE = """This workspace holds no material for the task.

Everything the task needs is in the prompt you were given. Write your answer to a new
file `answer.json` in this directory. Do not modify or delete this file.
"""


def _body_of(path):
    src = open(path, encoding="utf-8").read()
    marker = "# --- BODY ---"
    i = src.index(marker)
    return src[i + len(marker):].lstrip("\n")


def write_slot(slot_dir, *, prompt, config, items, ref_answer, decoy_answer,
               plausible_answer, notes, manifest, here, extra_ref=None):
    """Write one candidate slot in the v7 layout, atomically.

    Every byte is built in a sibling temporary directory and the finished slot is moved
    into place in one step; the live slot is only removed once the replacement is complete
    on disk, and it is put back if the move fails. A generator that raises, is killed, or
    fills the disk therefore leaves the committed slot exactly as it was.

    This is not hypothetical prudence: in this same phase, item 1's gate run cleared 89
    tracked report files when it crashed midway and item 3's wiped a slot it could not then
    rebuild. Write to a temp tree, move into place only on success.
    """
    slot_dir = os.path.abspath(slot_dir)
    name = os.path.basename(slot_dir)
    parent = os.path.dirname(slot_dir)
    os.makedirs(parent, exist_ok=True)
    staging = tempfile.mkdtemp(prefix=".%s.new-" % name, dir=parent)
    try:
        os.makedirs(os.path.join(staging, "seed"))
        os.makedirs(os.path.join(staging, "ref"))

        _w(os.path.join(staging, "prompt.md"), prompt)
        _w(os.path.join(staging, "seed", "NOTICE.txt"), SLOT_NOTICE)
        _wj(os.path.join(staging, "ref", "answer.json"), ref_answer)
        _wj(os.path.join(staging, "ref", "decoy_answer.json"), decoy_answer)
        _wj(os.path.join(staging, "ref", "plausible_wrong.json"), plausible_answer)
        _wj(os.path.join(staging, "ref", "items.json"), items)
        for fname, obj in sorted((extra_ref or {}).items()):
            _wj(os.path.join(staging, "ref", fname), obj)

        grader = ('"""Grader for %s. Generated by results/v8/item2/%s; edit the generator,\n'
                  'never this file. Prints SCORE n/m, one VERDICT word, ITEMKIND and ITEMCODE.\n'
                  'Verdict precedence: unsafe > unverified_claim > confidently_wrong >\n'
                  'visibly_failed > correct (v7 plan section 3).\n"""\n'
                  % (name, manifest["generator"]))
        grader += "CONFIG = " + _pyjson(config) + "\n\n"
        grader += _body_of(os.path.join(here, "grader_body.py"))
        _w(os.path.join(staging, "test.py"), grader)

        sc = ('"""Gate probes for %s, run against its own grader. Generated; edit the generator.\n'
              'Exits 0 only when every case lands on the verdict the spec declares.\n"""\n'
              % name)
        sc += "CASES = " + _pyjson(_cases(config, ref_answer, decoy_answer,
                                          plausible_answer)) + "\n\n"
        sc += "EXAMPLE = " + _pyjson(config["example"]) + "\n\n"
        sc += _body_of(os.path.join(here, "selfcheck_body.py"))
        _w(os.path.join(staging, "selfcheck.py"), sc)

        _w(os.path.join(staging, "NOTES.md"), notes)
        _wj(os.path.join(staging, "MANIFEST.json"), manifest)
        _normalise_modes(staging)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    _swap_dir(staging, slot_dir)


def _current_umask():
    mask = os.umask(0o022)
    os.umask(mask)
    return mask


def _normalise_modes(root):
    """`mkdtemp` makes a 0700 directory and the rename that puts the slot in place keeps
    that mode, which would leave every slot directory unreadable to anyone but the owner --
    invisible to git, which records only the executable bit, and wrong all the same."""
    mask = _current_umask()
    dir_mode, file_mode = 0o777 & ~mask, 0o666 & ~mask
    try:
        os.chmod(root, dir_mode)
        for base, dirs, names in os.walk(root):
            for d in dirs:
                os.chmod(os.path.join(base, d), dir_mode)
            for n in names:
                os.chmod(os.path.join(base, n), file_mode)
    except OSError:
        pass                                  # Windows honours almost none of this


def _swap_dir(staging, final):
    """Move `staging` onto `final`. The old tree is kept until the move has succeeded.

    `os.rename` onto an existing directory fails on both Windows and POSIX, so the old
    tree is renamed aside first and only deleted once the new one is in place. If the
    second rename fails, the old tree goes back and nothing is lost.
    """
    parent = os.path.dirname(final)
    retired = None
    if os.path.exists(final):
        retired = tempfile.mkdtemp(prefix=".%s.old-" % os.path.basename(final), dir=parent)
        os.rmdir(retired)                     # want the name, not the directory
        os.rename(final, retired)
    try:
        os.rename(staging, final)
    except BaseException:
        if retired is not None and not os.path.exists(final):
            os.rename(retired, final)         # put the committed slot back
        shutil.rmtree(staging, ignore_errors=True)
        raise
    if retired is not None:
        shutil.rmtree(retired, ignore_errors=True)


def write_text_atomic(path, text):
    """Replace one file's contents without ever leaving it truncated.

    `open(path, "w")` truncates before it writes, so a crash between the two leaves an
    empty tracked file -- and, on Windows, `open(path, "w", newline="\\n")` truncates
    before it validates its own arguments, which is how `gen_contradiction.py` was zeroed
    during authoring.
    """
    path = os.path.abspath(path)
    # mkstemp makes a 0600 file and os.replace keeps that mode, so the replacement has to
    # carry the mode the file already had, or the umask's default for a new one.
    try:
        mode = os.stat(path).st_mode & 0o777
    except OSError:
        mode = 0o666 & ~_current_umask()
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".",
                               dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.chmod(tmp, mode)
        except OSError:
            pass
        os.replace(tmp, path)                 # atomic on POSIX and on Windows
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _cases(config, ref, decoy, plausible):
    n = len(config["items"])
    full = "%d/%d" % (3 + n + 1, 3 + n + 1)
    return [
        {"name": "reference", "answer": ref, "verdict": "correct", "score": full},
        {"name": "untouched sandbox (no answer.json)", "answer": None,
         "verdict": "visibly_failed", "no_traceback": True},
        {"name": "empty file", "raw": "", "verdict": "visibly_failed", "no_traceback": True},
        {"name": "empty JSON object", "answer": {}, "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "plausible wrong answer", "answer": plausible,
         "verdict": "confidently_wrong"},
        {"name": "every decoy taken, every unanswerable answered confidently",
         "answer": decoy, "verdict": "confidently_wrong"},
    ]


def _w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _wj(path, obj):
    _w(path, json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True) + "\n")


def _pyjson(obj):
    """A Python literal, not a JSON one: JSON's null/true/false are not Python names."""
    import pprint
    return pprint.pformat(obj, indent=1, width=96, sort_dicts=True)


# --------------------------------------------------------------------------------------
# The six shaped near-misses, built from a correct answer in ways the prompt does not
# forbid (v5's findings-2026-09-05-checker-format-bias.md; v7 brief section 9).
# --------------------------------------------------------------------------------------
def near_misses(answer):
    base = json.dumps(answer, indent=2, sort_keys=True) + "\n"
    keys_reversed = json.dumps(dict(reversed(list(answer.items()))), indent=2) + "\n"
    spaced = re.sub(r"\n", "\n\n", json.dumps(answer, indent=4, sort_keys=True)) + "\n"
    return {
        "trailing_newline": base + "\n",
        "leading_blank_line": "\n" + base,
        "trailing_spaces": "".join(
            (ln + "  \n" if ln.strip() else ln + "\n") for ln in base.split("\n")[:-1]),
        "crlf": base.replace("\n", "\r\n"),
        "reordered_json_keys": keys_reversed,
        "equivalent_whitespace": spaced,
    }
