# Pending

Open manual cleanups and known-unfixed faults, and nothing else. Each item
records where it was found and where the fix has to happen. Clearing an item
means editing it out in the same commit as the fix; if its diagnosis is worth
keeping, it moves to `fixed.md` rather than staying here.

Swept 2026-09-10, when pi-slb, the worker runtime and the supervisor were
retired: every item that was open work on that machinery went with it, since
the code it named is no longer in the tree or on any host. Seventeen items came
out. What the runtime measured before it was deleted is
`agent-runs-sweep-2026-09-10.md`; the design and unit pages stay in `org/` as
history, and `deeper-docs.md` marks them retired. Nothing below is a v0.3
item.

The Windows converge that had been owed since its 2026-09-10 MSI 1601 failure
also came out, because it ran: the machine had been rebooted in between (CBS
`RebootPending` read False at 15.5 h uptime), `Microsoft.PowerShell` skipped as
already converged, and the full
`--tags bootstrap,packages,app_config,dotfiles,windows_verify` pass finished
`ok=149 changed=19 failed=0` with `windows_verify` green.

## Open questions and held work

- [ ] **v7 bench: nine slots admitted, residual work banked.** Protocol and
      registry: `results/v7/authoring/roundtable.md` in local-llm-bench.
      Open: phase-2 m10 is two cells short of n=20 (rerun, append to
      `results/v7r6-accept-IQ2_M-main.json`, never overwrite, then the n=20
      tallies and Wilson update); m08 fix round 1 (class-3 in-spec assert per
      the GLM REVISE; brief at `org/evidence/v7-brief-m08-fix1.md`)
      then the Opus admission leg; phase-1 cross-card Spearman; the pibench
      `:916` void filter and config-block recording as their own reviewed
      edit; the m-slot Windows-leg admission record check
      (`stage_gate_suite.py` stages only q-slots, so m-slot Windows legs never
      ran); the roundtable closing section. Forward plan:
      `org/v7-campaign-plan-2026-09-08.md`.
      Two of these were confirmed **unwritten rather than stranded** on
      2026-09-11 (`sync-audit-2026-09-11.md`): the string `void` appears
      nowhere in `pibench.py` on any tree on any host, and the two missing
      m10 cells exist nowhere — origin has m10 at 18 rows and the desktop's
      dirty copy is staler still at 10. Neither is waiting on an unsynced
      machine.

- [ ] **Desktop `D:\local-llm-bench` is 32 behind with 57 dirty entries.**
      Audited path by path on 2026-09-11: every entry is a duplicate, a stale
      prefix of a file origin already holds, or regenerable staging, so
      **nothing in it is at risk** and no commit is owed from it. It does not
      self-heal — `Clone_Repos` skips dirty worktrees by design, so every
      converge leaves it behind and says so. Clearing it means discarding the
      working tree and pulling, which is destructive and was left for the
      owner. Evidence: `sync-audit-2026-09-11.md`.

- [ ] **Two tracked copies of the q09 candidate disagree inside origin.**
      `results/v7/authoring/r5/gate-suite/q09-main-glm/` and
      `results/v7/authoring/cand-glm/q09-main-glm/` are both tracked, both 92
      files, and differ in 45 entries: the corrected candidate was restaged
      into the gate-suite copy on the desktop and that fix was never
      committed. Harmless if `r5/gate-suite/` is regenerable staging the way
      `r2/gate-suite/` is, but `r5/gate-suite/` is tracked, so the repository
      currently ships both versions and nothing says which the gate ran.
      Found by the 2026-09-11 sync audit.

- [ ] **Downloader: cookies are the owner's call, and only if needed.** No
      cookie jar exists anywhere in the fleet and cachy pulls cookie-less. If
      YouTube starts answering cachy with a bot check, the owner decides
      whether to create the secondary account and hand-place a private-window
      jar per `skills/downloader`; nothing else is tried first. Still left for
      the owner: `C:\Users\slb\Downloads\cachyos-first-contact`.

- [ ] **Qwen3.8 Flash trial, owner-ruled and not yet run.** Route: OpenRouter
      `qwen/qwen3.8-flash`, sole provider Alibaba Cloud Int. at $0.15 / $0.47,
      1M context, no training but retains prompts, so the trial needs a
      per-model ZDR exemption in the managed pi `modelOverrides` and a
      `max_price` ceiling ($0.375 / $0.94). Nothing else on the survey list is
      cheap enough. Reports:
      `org/evidence/{hy4-control,control-candidates}-report.md`.
      One thing changed under it on 2026-09-10: the `pi-run` wrapper that used
      to refuse an uncapped model before launch is gone, so the ceiling is now
      policy in the managed `models.json` and nothing checks it beforehand.

- [ ] **Owner's hand step still owed on cachy:** `codex login`. The other two
      gaps `pi-slb-acceptance-2026-09-07.md` named were an inbox route from
      cachy to wsl for waking a control root, and the runtime that would have
      done the waking; both left with the runtime.

- [ ] **Org-doc sweep: three findings open, none blocking.** Full table:
      `org/evidence/org-doc-sweep-2026-09-08.md`. Open:
      `README` claims the estate is "all provisioned by this repository" while
      the Tailscale console and manual publishing are not;
      `bench-v4-carryover-2026-09-03.md` prescribes blocking and detached
      launch the current contract rejects (dated page: addendum only, never a
      rewrite); `wrt-trial-results-2026-09-04.md` cites a document dated a day
      after it. The fourth — "`README` says three roles where the design names
      four" — closed on 2026-09-10 from the other side: the design that named
      four is retired and the contract now names two, the control session and
      a worker, with `org/README.md` and `agent_config_instructions` agreeing.

- [ ] **DeepSeek: the served build is not identified, and the rate card is
      still the owner's call.** The V4.1 identity claim was withdrawn
      2026-09-10 (`4ef2cd1`) after a cross-family check refuted the seat's
      effort-enum argument twice; the evidence and the lesson are in
      `org/deepseek-v41-2026-09-09.md` under `## Correction, 2026-09-10`, and
      the rule it produced is rule 10 in `org/web-research-briefs.md`. What is
      measured and correct stands: the id `deepseek-flash`, all seven effort
      values, `none` alone without `reasoning_content`, and the 1048576 /
      393216 ceilings. Two things are open. The `cost` block carries DeepSeek's
      **off-peak** V4-Flash figures, and peak is double from 01:00-04:00 and
      06:00-10:00 UTC Monday to Friday — this fleet's working evenings — so the
      encoded cost understates a large share of real runs; switching to the
      peak figures is the conservative encoding and was left rather than
      changed unilaterally. And the card's whole justification was "billed at
      V4-Flash rates", which rested on the identity now withdrawn, so it is
      weaker evidence than when it was approved.

- [ ] **Codex auto-compaction may not fire under headless `codex exec`.**
      `openai/codex#16033` is open: compaction reported as not triggering in
      exec mode even with the threshold well below the window, with
      `input_tokens_used` empty in the session log. This fleet spawns every
      Luna worker through that path, and `agent_config_codex_config` now
      declares `model_context_window = 1000000` with a 700k threshold, so a
      worker that does not compact runs to the real 1,050,000 ceiling and
      takes a context-length rejection instead. Unverified on this fleet —
      no worker here has yet run deep enough to test it. Watch for a worker
      dying late in a long run, and check `codex --version` against the
      issue before blaming the brief. The sibling defect `#16068`
      (`fill_to_context_window` poisoning the token counter after a context
      overflow) is held out of reach by the threshold sitting at 70% of the
      declared window, so compaction fires before the overflow path can run.

- [ ] **cachy's scratch 1080 Ti benchmark install was deleted, unexamined, and
      is not recoverable.** On 2026-09-10, a cleanup pass removing the retired
      runtime's residue ran `rm -rf ~/.local/state/control-scratch` on every
      Linux host. On wsl that directory held 1.9 MB of v0.3 gate scratch, which
      was inspected first and was duplicate. **On cachy it held 33 GiB and was
      not inspected** — the same script was pointed at three hosts after
      checking one. What it was is known only from
      `glm-seat-audit-2-notes.md:3955`, which recorded a survey of that path on
      2026-09-08: a scratch Vulkan Ollama build plus `qwen3:8b Q4_K_M`, staged
      under `control-scratch/cachy-1080ti` for the 1080 Ti bench arm.
      Not recoverable: `/home` is the btrfs subvolume `@home`, snapper
      snapshots cover the root subvolume only, and there are no `@home`
      snapshots. The btrfs data allocation on `/home` now shows 44.01 GiB
      allocated against 30.63 GiB used, which is the freed-chunk signature of
      the delete.
      Re-creatable rather than lost work: Ollama installs and `qwen3:8b Q4_K_M`
      re-pulls, and no Ollama model is ansible-managed anywhere on this fleet.
      The **managed** Ollama on cachy was never touched — service active and
      enabled, `/usr/bin/ollama` intact. Whoever resumes the 1080 Ti arm rebuilds
      the scratch install; nothing else on cachy depends on it.
      The rule this cost: **look at the target on every host, not on the first
      one.** A path that is scratch on the controller is not scratch everywhere,
      and a size check is not an inspection.

- [ ] **slbh is deployed as an application; whether it becomes a fourth
      *managed* harness is the owner's call and has not been made.** Since
      2026-09-10 the fleet compiles `~/slbh` into `~/.local/bin/slbh` on every
      target (`dotfiles`, `windows_dotfiles/tasks/slbh.yml`). Nothing else
      about it is managed: no `agent_config_*` entry, no `agent_skills` entry,
      and its own config is `$SLBH_HOME/config.json`, written by its `/models`
      flow rather than by a play. That is deliberate while features are still
      in development — a managed file would fight the TUI that writes it — and
      it is the shape ProfLM and CoachLM already have. Adopting it as a fourth
      harness means deciding what of that config the fleet owns, and would
      change `org/agent-harnesses.md`, which is binding.
      Two facts to carry into that decision. Its provider keys —
      `DEEPSEEK_API_KEY`, `ZAI_API_KEY`, `OPENROUTER_API_KEY` — were already
      in the exported `api_keys` tier, so the deploy needed no new secret and
      adopting it needs none either. And **the Windows build is degraded by the
      project's own account**: slbh targets Linux, and its non-Linux build uses
      a shell fallback with no Linux process-group semantics. It is deployed on
      Windows because the fleet deploys everywhere; it is not equivalent there,
      and nothing measured how far from equivalent. The local provider is now
      an approved application route, not a managed harness: it uses no key,
      points at the Windows desktop's Tailscale-bound Ollama, and defaults
      leaves to `local/q27-IQ2_M-96k`; a devbox-originated `/v1/models` check
      verified that route on 2026-09-11.

## Known-unfixed faults

- [ ] **devbox: the `resolver` role's Quad9-over-DoT pin is not on the host.**
      Found 2026-09-10 while answering a question about DNS routing, not by a
      failing play. `resolvectl status` on the devbox reports eth0 with
      `DNS Servers: 185.12.64.2 185.12.64.1 2a01:4ff:ff00::add:2
      2a01:4ff:ff00::add:1` and `-DNSOverTLS` — Hetzner's own DHCP resolvers,
      in the clear — and `nmcli -g ipv4.dns,ipv4.dns-options,ipv4.ignore-auto-dns
      con show "cloud-init eth0"` returns empty, empty, `no`. The role writes
      exactly those three, so the profile has been reverted to DHCP at some
      point; nothing here knows when or by what.
      **Not a live leak.** `resolv.conf mode: stub`, and tailscale0 holds the
      `~.` routing domain with `100.100.100.100`, so every query still leaves
      through tailscaled's DNS over HTTPS to Quad9. What is gone is the
      fallback the role exists to provide: with the pin reverted, a tailscaled
      outage drops the box to plaintext port 53 to Hetzner instead of Quad9
      over TLS.
      The fix is one converge, `./devbox.sh --tags security`, which is the tag
      `resolver` carries — `Configure_Resolvers` re-pins, `Reapply_Default_
      Connection` applies it live, and `Require_Resolvers_Active` asserts a
      real query through it. It is unrun because the recent devbox converges
      were `--tags dotfiles`, which cannot reach that role. Held for the
      owner only because the same tag re-converges the firewalld zone and the
      sshd drop-in on the host the controller reaches over that very link.

- [ ] **`Validate_Controller_Toolchain` blames the wrong thing when it
      fails.** `roles/windows_preflight/tasks/main.yml:35` loops over
      `windows_controller_versions.collections`, but each iteration asserts
      all seven conditions, four of which have nothing to do with the loop
      item. Its `fail_msg` interpolates `{{ item.key }}={{ item.value }}`, so
      a missing `ansible_lint` reports as
      `Controller postcondition failed for community.windows=3.3.0` — naming
      a collection that was fine. Ansible's own `assertion` field carries the
      truth, but the message is what an operator reads. Observed 2026-09-09
      running `windows.yml` outside the pinned venv. The fix is to split the
      four fixed conditions into their own unlooped task; the preflight is
      otherwise correct and refused before changing anything, which is the
      behaviour the role is for.

- [ ] **Targets carry an Ansible install the secrets model says they never
      see.** `roles/user_tools/tasks/main.yml:264` (`Install_Ansible`, pipx,
      `install_deps: true`) runs on every host in the role, so devbox and cachy
      hold `~/.local/bin/ansible-playbook` and `ansible-vault`. No
      `.vault_pass` exists on either, so nothing decrypts and a stray
      `ansible-playbook` on a target dies on the vault. The org map's secrets
      model line 2 ("targets never see the vault or Ansible") is false as
      written. Fix one side: gate the two installs on the controller and let a
      converge remove them, or reword the map to "targets never run Ansible".

## Standing lessons

- [ ] **A deletion task that names no file it deleted has not been tested.**
      `Purge_Stripped_Skill_Paths` shipped to strip `holder.py` and
      `ledger.py` from every deployed skill root. It looped over
      `dotfiles_agent_skill_dirs` — each *skill's* directory — against paths
      that are relative to the *root* the skills sit in, so it built
      `~/.claude/skills/org/pi-slb/scripts/holder.py` and 135 more like it,
      matched none of them, and reported ok on every converge. Two separate
      audits then read the surviving files as evidence that no purge mechanism
      existed, and one fix corrected a path inside a list the loop could never
      reach. Nothing caught it because a `state: absent` loop is green whether
      or not the path was ever there. Corrected in both roles, with
      `windows_verify` now asserting the absence, which is the only check that
      could have failed. When a task's whole purpose is removal, prove it
      removed something once, by hand, on a host that had it.
      The 2026-09-10 retirement is the same shape one level up and took the
      same precaution: dropping a shim from `agent_bin_shims` stops deploying
      it and removes nothing, so the four withdrawn verbs are named in
      `agent_bin_shims_retired` with an absence assert behind them.

- [ ] **Withdrawing a table from a merge-managed file does not remove it.**
      `~/.codex/config.toml` is rebuilt from the managed head each converge and
      the host's own tables are carried over, so a block the managed text
      stops naming stops being managed and lives on that host forever. The
      2026-09-10 retirement had five `[[skills.config]]` entries to withdraw
      and kept a sixth, `close-up-shop`, for exactly this reason: one surviving
      block keeps `[[skills.config]]` a managed header, and the tail filter
      rejects every tail block repeating a managed header. Delete the last one
      and all six come back as unmanaged tail. The same trap has a different
      answer for pi's `settings.json`, which is key-merged rather than
      block-merged: `agent_config_pi_settings_retired`.

- [ ] **A document that declares itself not a plan needs a counterpart that is
      the plan, in git, named from the index, before the work starts.** A
      design whose charter is "not a plan" leaves staffing and sequencing with
      nowhere to go, so they go to `control-scratch`, which is not version
      controlled and which nothing points at. Findings then get filtered by
      "is this design?", and the purely operational ones are dropped by that
      filter even when they are the most actionable thing measured.

- [ ] **A steer states what to keep, and the clause is the remedy.** An
      identical mid-run steer without a keep-clause makes Luna discard its
      entire briefed output and return only the new item, while GLM keeps its
      work and adds the new conclusion; both obey, one destroys what it had
      already done. With an explicit keep-clause both preserve the earlier
      output in full. Measured twice without the clause and once with it;
      figures in `pi-slb-v0.3-rehearsal.md`. Every steer names what survives
      it, in as many words. Since 2026-09-10 the worker instruction set says so
      from the other side too, so a worker preserves its work by default.

- [ ] **Acceptance and delivery are two different facts, and most callers see
      only the first.** The retired `agent-msg` printed a receipt at send time
      while the supervisor wrote the delivery record later, when the message
      was actually taken, so a caller reading only the receipt could not tell
      whether its correction reached the worker before or after the work it was
      trying to stop. `inbox` has the same shape and the same gap: a send
      appends to the recipient's mailbox and says so, which is not the same as
      the recipient having read it.

- [ ] **A validation script whose failure path prints instead of exiting
      non-zero is a validator that cannot fail.** A validation job's exit code
      read green while the measurement step had swallowed its own
      `ERR_MODULE_NOT_FOUND`; only the log showed it. Exit non-zero from every
      failure path, and read the log even when the job is green.

- [ ] **A count reported behind a filter carries its denominator, broken out
      by the field filtered on.** `334 inspected, 0 matched` is
      indistinguishable from `334 inspected, nothing to find`. An audit brief
      filtered on a manifest value no run on this host carries and returned a
      clean "Findings: none"; its exposure metric compared log length against
      answer length, so a zero-byte log scored identically to a clean run.
      Three instances of the same shape in one audit. Applies to every brief.

- [ ] **Verify a permanence claim by waiting out the falsifying interval, not
      by grepping one writer.** An escalation that mint-abandoned stubs were
      permanently non-terminal and blocked the close was wrong and was
      withdrawn: the holder outlived the launcher and promoted the stub. Every
      citation in it was true and the conclusion was not.

- [ ] **A converge log piped through `tail` is a log nothing can be diagnosed
      from.** Three Linux converges were captured as `./host.sh ... | tail -12`,
      which keeps the recap and throws away every `changed:` line, so a
      `changed=1` on WSL could not afterwards be attributed to a task. The
      habit contradicts this repo's own standing rule that an answer is read
      whole and never from a stdout tail. It was also load-bearing in a way
      that hid it: a backgrounded command here gets non-blocking stdout, which
      Ansible refuses outright, and the pipe was incidentally supplying a
      blocking handle — so dropping the pipe broke the play and looked like an
      unrelated fault. Redirect to a file: blocking, and complete.

- [ ] **Do not edit a file a measurement is reading.** A ruling appended to
      the design mid-rehearsal, after one worker had finished and while
      another was still reading, made their per-section counts incomparable.
      The same applies one step earlier: a page describing a measurement does
      not enter the tree while the subject of that measurement can read it.
