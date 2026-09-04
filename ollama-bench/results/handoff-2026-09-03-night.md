# Control session handoff, 2026-09-03 night

Restart source for the next control session. **Supersedes and replaces both earlier handoffs of this
date** (morning and evening), which were deleted after their contents were checked forward — the
morning one's only unique loose end, the doc edit describing the phone-attached session as the
owner's away path, is already done (`org/README.md:76` names Claude Remote Control;
`skills/inbox/SKILL.md` mentions only the phone *key*). `results/v5/decisions.md` is the durable
ruling archive and `results/inbox-archive-2026-09-03/` is kept.

Owner: slb (they/them), reached through Claude Remote Control. Phone relay retired; never send to
phone@fractal.

## State at handoff (~18:45)

- **ansible-slb: `d9cd381 retire cursor remnants` on main, pushed.** Both clones at `d9cd381`, both
  clean. Converged after the change on all three hosts, `failed=0` everywhere: WSL 76/3/0,
  Windows 150/2/0, devbox 125/4/0. Windows `Verify_Agent_Config` and `Verify_Agent_Skills` both
  pass, which is the byte-hash proof the deployed skills match source.
- **What landed in that commit:**
  - **Improvement item 15 closed.** The Cursor retired-path lists and their tasks deleted outright
    — `user_tools_retired_paths`, `dotfiles_retired_agent_paths`, `windows_retired_agent_paths`,
    `windows_retired_path_dirs`, and the tasks `Remove_Retired_Cursor_Cli`,
    `Remove_Retired_Agent_Config`, `Remove_Retired_Vendor_Packages`,
    `Verify_Retired_Agent_Removal`. All eight names are now zero repo-wide. The precondition was
    verified on every host first (paths absent on WSL and devbox, `enabledModels` absent from pi
    settings, Windows verify green).
  - `agent_config_pi_settings_retired` emptied to `[]` with the **mechanism deliberately kept**
    (the Linux `rejectattr`, the Windows per-file retired-key list, the `windows_verify` absent
    assert). CLAUDE.md makes that the standing rule for withdrawing a key from any merge-managed
    document, so only the entry left. An empty list is a verified clean no-op on all three paths.
  - `skills/inbox/scripts/inbox`: the header comment claiming deployment into "all three skill
    roots" including `~/.cursor/skills/inbox/` corrected to two — it contradicted CLAUDE.md's
    "There is no third skill root" — and `cursor` dropped from the `--harness` allowlist, now
    `claude|codex|pi|other`.
  - `org/agents.md`: the heredoc note under **Claude Code** (see standing constraints).
  - CLAUDE.md and AGENTS.md re-synced, byte-identical apart from the title line.
- **v5 planning lives in `ollama-bench/results/v5/` in this repo.** Corrected 2026-09-04: the
  un-versioned `~/ollama-bench` scratch this line described was folded into `local-llm-bench`
  and no longer exists on any host.
  - `results/v5/plan-rev5-focused.md` is **rev 5.4** and is the plan to execute.
    `plan-2026-09-03.md` (rev 4) stays on disk as the harness reference only.
  - `results/v5/schedule.md` created: the three queued GPU runs with reasons, the standing run
    rules, and a log.
  - `results/v5/decisions.md` carries every ruling, latest at the bottom.
- **Authoring has NOT started.** Phase A waits on the owner's go-ahead.
- GPU idle, no model loaded, no benchmark process running.
- Usage at handoff: 5h 28%, weekly-all **84%** (warning), Fable-scoped **94%** (critical and
  active), both resetting 2026-09-05 ~08:00 MDT. Control ran on Opus for exactly that reason.

## Owner rulings this session (all in results/v5/decisions.md)

- **u04 (Unity EditMode tests) cut.** Suite is nine tasks, headline seven (u01-u03, g01-g04). The
  verdict arity followed: viable at three quarters of a class's headline tasks rounded up, marginal
  at half rounded up — general (4) viable at 3, Unity (3) viable at 3. Requiring 3/3 for Unity is
  deliberate; at three tasks a 2-of-3 bar lets one task carry a class.
- **B0 probe is IQ3_M at 32k** — the plain `q27-IQ3_M` with `num_ctx 32768, num_gpu 66`, not the
  baked `q27-IQ3_M-64k`, because 32k is 13.39 GB with ~2 GB margin where 64k is 14.11 GB and
  fair-weather. Decided on `results/gpu-tune/summary.md`, which rev 5.2 had never absorbed; the
  earlier Q3_K_M recommendation was withdrawn as resting on a stale premise.
- **IQ3_M is where the search starts and explicitly NOT the org's quality answer.** The owner is
  unconvinced on quality grounds. That is structural in the plan, not a footnote: B1 gives Q3_K_M
  and Q2_K_L the **full seven-task headline set** rather than a sentinel subset derived from
  IQ3_M's own passes, the B0 fallback gate is Q3_K_M rather than Q3_K_S, and B2 picks the winner
  "on the evidence, not by seniority".
- **q8_0 KV control: yes.** New Phase B0-control, ~15 min, on g05 plus the two highest-partial-score
  headline tasks that failed under q4_0. It carries its own revert step — the env var goes back to
  `q4_0` and Ollama restarts, or the baked `*-64k` models exceed VRAM.
- **"Is 2-bit viable at all for any real work" is a verdict line of its own**, reported whatever the
  ranking says, beside Q2_K_L's context reach (96k resident is a capability nothing else on this
  card has). Q2_K_L earns it with the full headline set in B1 and is the named Phase D concurrency
  candidate whatever wins B2.
- **Q3_K_L dropped from v5** as a recorded decision. **IQ2_M** raised as a conditional only, brought
  back if Q2_K_L lands marginal rather than clearly dead.
- **`cursor` dropped from the inbox `--harness` allowlist.**
- **Leave the plan; Phase A unstarted; wind the session down.**

## Pending

1. **Phase A go-ahead — the live question.** Phase A is: author nine tasks, selfcheck each (execute
   every example list, then Haiku x3 for prompt defects), gate Sonnet 3/3 and GLM 2/3, record
   hashes, then the four reference rows at three trials each. GLM is under USD 2 and Luna rides the
   ChatGPT window, but Sonnet, Haiku **and any Opus worker doing the authoring** all draw on
   weekly-all, at 84% with the reset on Saturday.
2. Improvement item 20, second half: local quant roster rows in `org/models.md` after v5 phase B.
   (First half — the DeepSeek v4 column — is done.)
3. `D:\avatars` M3 fix stays **UNCOMMITTED** until the campaign ends: 3 dirty files under
   `tools/bench/`, untouched this session and verified still dirty.
4. Claude-usage alerts at 85% and 95% weekly-all. The Fable-scoped sub-limit is already 94%
   critical; keep Control on Opus until the Saturday reset.
5. `org/pending.md`: two Tailscale admin-console cleanups still open (the dead `desktop-g27mv3l`
   node, the orphaned `fractal` node on the gmail tailnet) and the devbox Fastly IPv6 stall.

## Standing constraints

Never edit `~/.pi`, `~/.claude/skills`, `~/.agents/skills` or `~/.codex` by hand — ansible-managed,
and a converge is the only thing that changes them. The WSL clone `/home/slb/ansible-slb` is the
only controller; a non-`org` change reaches a play only from that clone; `org/**` is the one
carve-out editable from either. Drive WSL from Windows with
`MSYS_NO_PATHCONV=1 wsl.exe -- bash -l /mnt/c/Users/slb/.claude/tmp/<script>.sh`; ansible-lint only
in WSL. **A multi-line program never goes through a heredoc in the Bash tool** — quoting in the body
breaks the outer command and the shell error names nothing in the script; write it to a file and run
the file (now recorded in `org/agents.md`). Never export `CODEX_API_KEY` or `ANTHROPIC_API_KEY`; the
OpenRouter key goes nowhere but openrouter.ai; never paste keys. One model on the GPU at a time.
Judge a local config by measured tok/s, never by reported residency. Commits only as the owner, 1-5
lowercase words, one line, never as a contributor. Delegate well-defined work to Opus workers and
verify what comes back. No `pi-run` or `codex-run` from inside a pi or Codex run
(`AGENT_RUN_DEPTH`). `manage_tools "sync"` forbidden. restic barred for agents, except the
`D:\avatars` backup. Read `~/ansible-slb/CLAUDE.md` and the org index on entry and after every
compaction.
