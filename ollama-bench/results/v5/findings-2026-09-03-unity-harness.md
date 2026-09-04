# Finding: the v5 Unity harness does not exist as the plan describes

Found 2026-09-03 by the control session on restart, verifying Phase A's prerequisites before
asking for the go-ahead. Nothing has been run and nothing in the plan has been decided against
this; it is written down so the gap is not discovered by whoever authors u01 to u03.

## What the plan claims

`plan-rev5-focused.md`:

- line 71 — "Unity tasks run against the bench-C project with the batchmode compile loop from
  rev 4 section 8."
- line 76 — u01's checker is "batchmode compile + play-mode test"; u02 is "compile + reflection
  check of members used"; u03 is "compile + asset reference check".

## What is actually on disk

- **Rev 4 has no section 8 Unity content and no Unity content at all.**
  `plan-2026-09-03.md` is 204 lines; `grep -i unity` over it returns nothing, and its section 8
  is "If this session dies". The citation is dangling.
- **bench-C is real**: `D:\VRCA-Bench\projects\bench-C`, beside `bench-A` and `bench-B`.
  It is a full Unity project (Assets, Library, its own CLAUDE.md, generated .csproj files).
- **There is no batchmode compile loop in the bench tooling.** The runner is
  `D:\avatars\tools\bench\bench\runner.py`, invoked as
  `python -m bench.runner run --tasks a,b --models haiku,sonnet,opus,fable --trials 2
  --editors A,B,C`. It drives **live Unity editors over the MCP-for-Unity hub**, one clone
  project per editor. `grep -rn batchmode` over the whole of `tools/bench` hits only two
  reference documents under `bench/contestant/skills/` describing
  `Unity.exe -batchmode -nographics -executeMethod` as a general Unity technique. No harness
  code invokes it.
- `results/v5/decisions.md:11` records the ruling that matches the tooling —
  "Q12 gates: Unity gates through the VRCA-Bench runner with claude -p contestants" — and
  `decisions.md:126` refers to "the 3-editor loop". So the live-editor loop is the decided
  mechanism and the plan's line 71 is simply a mis-citation.

## Why it matters before Phase A, not after

Three consequences, in order of how much they cost.

1. **u01 to u03 are three of the seven headline tasks and one of the two verdict classes.**
   Under section 7's arity rule the Unity class is viable only at 3/3, so all three tasks have
   to work or the class reports not viable for a harness reason rather than a quant reason.

2. **The local arms run through pi, and pi cannot pick a Unity editor.** The hub routes by an
   `unity_instance` argument its tool schemas do not declare while declaring
   `additionalProperties: false`; pi validates tool arguments against the schema and refuses to
   send it (ansible-slb `CLAUDE.md`, measured 2026-09-02). One editor connected and a pi Unity
   call works; more than one and every call returns `instance_selection_required`, whose only
   lever is the machine-wide `set_active_instance`. So **the three-editor parallelism is
   available to the `claude -p` reference arms and not to the local quant arms**, which are
   serialised on a single connected editor. Every prior v4/v5 local run through `pibench.py`
   was pure-file work, so the pi-plus-Unity combination has never been exercised here.

3. **A live editor is not a hidden checker.** Design rule 3 says the checker is hidden and
   contestant-authored tests never count. The VRCA-Bench runner already grades this way
   (`files_changed`, YAML reads off disk, gateway log parsing), so the machinery exists — but it
   is per-task Python against a live editor, not the `test.py` shape `tasks-v4/*/` uses. Authoring
   a Unity task is therefore materially more expensive than authoring a general one, and the
   plan's "about half a day" for Phase A was sized without that distinction being visible.

## What is not being claimed

That the Unity tasks are impossible — VRCA-Bench runs exactly this shape of task today
(`toggle-default-on`, `why-verypoor`, `texture-budget`, `builds-worse`), with a selfcheck
harness and completed runs against bench-C on haiku, sonnet, opus and fable. The claim is only
that the plan's stated mechanism does not exist, the real one has a pi-shaped limit on the local
arms, and the choice between them is the owner's rather than the authoring worker's.

## The options, for the record

- **Adopt the live-editor loop as written in `decisions.md`.** u01 to u03 become VRCA-Bench
  tasks in the existing runner's shape, and the local arms take them one editor at a time.
  Costs authoring effort; keeps all three Unity tasks and the class verdict.
- **Build a real batchmode compile checker.** Closest to what the plan's section 4 text
  promises, gives a hidden non-interactive checker in the `test.py` shape, and removes the pi
  editor-selection problem entirely — but it is new harness code the estate does not have, and
  a play-mode test in batchmode is more than a compile.
- **Cut the Unity class from v5.** The suite becomes the four general headline tasks plus g05
  and g06, the verdict is general-only, and the mission's "Unity and general programming first"
  is answered for half of itself. Cheapest and the biggest loss.
