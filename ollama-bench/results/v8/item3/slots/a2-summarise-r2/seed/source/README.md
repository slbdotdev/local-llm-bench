# org

The map of slb's personal computing estate: one human, all repos private under
github.com/slbdotdev (personal account, no GitHub organization), all
provisioned by this repository, ansible-slb.

**How to read it.** One current fact per line: complete on *what and where*,
silent on *why* and *how much*; a claim's evidence link is the answer, not this
file.

Path history for anything under `org/` needs `git log --follow`.

## Machines

The server is `devbox` everywhere: inventory host, ssh alias, tailnet hostname.

Tailnet: the `slb.dev` account, MagicDNS suffix `wyvern-temperature.ts.net`.
Dial peers by MagicDNS name, never a `100.x` literal — addresses move on
re-registration. A second personal account exists
(`belden.stephen@gmail.com`, `tail142f4c.ts.net`); a machine on it looks
healthy but is invisible to every peer, so confirm:
`tailscale status --json | jq '.CurrentTailnet'`.

Tailnet DNS: Quad9 global nameservers, "Override DNS servers" and MagicDNS on —
every node resolves through tailscaled over DNS over HTTPS. No play can write
it, so the devbox `tailscale`, `windows_tailscale` and `windows_verify` roles
assert it instead (CLAUDE.md).

### devbox

Hetzner Fedora cloud server, always on. Public 5.78.228.142, tailnet
100.x.x.x. Provisioned by fedora-devbox.yml, which connects as root and
creates `slb`, over the tailnet. Nothing is publicly exposed: the `devbox`
zone drops port 22 on the public address (`security_public_ssh`), so every
login rides the tailnet and the Hetzner console is the break-glass:
devbox-tailnet-only-2026-09-05.md. The `resolver` role pins Quad9 over strict
DNS over TLS on `cloud-init eth0`: devbox-resolver-audit-2026-09-02.md. The
devbox receives the common yt-dlp, Deno, ffmpeg, and EJS/provider packages,
but is not the downloader and never holds the downloader cookie jar.

### FRACTAL

Windows 11 desktop (computer name FRACTAL, tailnet node `fractal`,
100.x.x.x) plus its Ubuntu WSL2 distro. Windows is provisioned by
windows.yml driven FROM WSL over WinRM/PSRP (`./win.sh`); the WSL side by
wsl.yml, locally. Fresh installs use the windows-oobe USB path, then `./wsl.sh`
and `./win.sh`.

Phone SSH over the tailnet lands in PowerShell 7. Linux and WSL targets carry a
managed `Host fractal` block dialing `fractal.wyvern-temperature.ts.net` over
IPv4 — the bare name resolves to the tailnet IPv6 address from Linux and sshd
there refuses it. Commands sent that way must be `sh -lc`, not `bash -lc`: pwsh
resolves `bash` to the WSL launcher and lands in the WSL distro instead.

`windows_tailscale` owns Tailscale and the host-side DNS boundary: outbound UDP
and TCP port 53 are blocked on every physical adapter carrying a default route,
and the tailnet resolver (`100.100.100.100`, `fd7a:115c:a1e0::53`) is pinned
statically there, so DNS fails closed when tailscaled stops. WSL inherits the
Windows resolver and MagicDNS; `windows_verify` re-checks it host-side:
windows-dns-leak-2026-09-03.md.
Exit node: a Mullvad Denver node. No play pins it, so which one drifts and this
map names none — Denver egress is the invariant; re-derive it per
fleet-audit-2026-09-04.md. `ANKI_BASE` resolves to `E:\Anki` by volume label
(`2000`), never by drive letter.

### Phones

galaxy-s25-edge (Android), iphone171 (iOS): tailnet clients. While away the
owner reaches sessions through Claude Remote Control, the bridge each Claude
Code session registers at startup. Phone SSH into FRACTAL still works, and such
a session hits the elevated-session trap under Agents.

### Dormant targets

fedora-desktop.yml has no machine on the tailnet and ubuntu.yml has an empty
host group. cachyos.yml has one host since 2026-09-06: cachy, the CachyOS box
on the house network, headless, reached as `ssh cachy` from every target with
its host key pinned in group_vars/all. `cachyos_headless` declares
`multi-user.target` and disables `plasmalogin.service` for the next boot. It
never sleeps: cachyos_power masks the systemd sleep targets and logind ignores
idle, keys and lid.

Machine ingress is Tailscale-only, the devbox included.
No containers, no CI/CD — deploys are ansible runs or git pushes.

cachy is the fleet downloader: it is the one member of the role-assignment
`downloader` group, so every fleet-dl dials it, and cachyos_tailscale asserts
it carries no Tailscale exit node.

## Services

- **CachyOS downloader** — the role-assigned fleet yt-dlp service with Deno,
  ffmpeg, and the bgutil PO-token provider on the house-network box; its
  per-host YouTube cookie jar is never managed by Ansible. The devbox is not a
  downloader and holds no cookie jar.

## Security posture

Enforced by ansible-slb. Only Windows has a dedicated re-check pass
(`windows_verify`); Linux targets rely on role convergence plus in-role
asserts, so there is no independent postcondition sweep there and a green Linux
recap is weaker evidence than a green Windows one.

- devbox: the firewalld `devbox` zone is DROP-target (ssh, dhcpv6-client,
  42128-42191/udp); tailscale0 rides the trusted zone.
- Windows: sshd key-only, firewall-scoped to the tailnet (100.64.0.0/10);
  WinRM 5985 scoped to the WSL NAT range (172.16.0.0/12), with the play
  dialing the MagicDNS name when the gateway address drops 5985 (fixed.md);
  RDP off; WSL runs no sshd; DNS boundary as under FRACTAL.
- Secrets exist only in ansible-vault; `.vault_pass` lives in Bitwarden, never
  in git.
- `vault_github_token` is a fine-grained PAT (Metadata read-only, all repos)
  with a 90-day expiration: created 2026-07-11, dies ~2026-10-09. On 401s, mint
  a like-for-like replacement and vault-edit it in.
- `vault_openrouter_api_key` has no expiry, so rotation is manual: mint,
  `ansible-vault edit`, converge every live host with `--tags dotfiles`, revoke
  the old key last. Last rotated 2026-09-02.
- `vault_zai_api_key` is the Z.ai GLM Coding Plan key (`ZAI_API_KEY`), minted
  on z.ai's API-key page under the plan; same rotation procedure.
- `vault_openrouter_management_key` can create and delete OpenRouter API keys,
  so it is never exported and never deployed: it stays in the vault and only
  `scripts/openrouter-activity.py` on the WSL controller reads it, for spend
  per model per UTC day.
- `scripts/plan-usage.py` reads live plan quotas and key-scoped OpenRouter
  spend; it never reads the vault and leaves `openrouter-activity.py` as the
  per-model tool.
- Commits are SSH-signed as slb <mail@slb.dev> since
  2026-07-10 (earlier ones used a retired PGP key and no longer verify).

The secrets model, in six lines (owner-confirmed 2026-09-06 after a session
got two of them wrong):

1. Controllers are WSL, and Windows through its own WSL. Only they hold
   `.vault_pass`, recreated by hand from Bitwarden, never on media or in git.
2. Targets (devbox, cachy) never see the vault or Ansible. Everything they
   hold arrives through a play from decrypted vault values; first contact on
   a new box needs only the two public keys in the committed vars file, and
   the repository is private, so a target cannot clone it and never needs to.
3. Every host gets the private fleet auth key, the signing key and the full
   provider key set by design; compromise of one host is compromise of the
   fleet's keys, and rotation is manual per key.
4. The OpenRouter management key never leaves the vault. The Codex login and
   the yt-dlp cookie jar never enter it: per-host, hand-placed.
5. GitHub, devbox and cachy host keys are pinned from the vars file; a new
   target's key is read off its own screen and pinned in the same commit as
   its inventory line, never keyscanned.
6. The connection user is the real login; system roles escalate with the
   vaulted become password, which is the account password set at install.
   No NOPASSWD anywhere, which is why there is no AUR.

## Repos

Non-archived repos are auto-cloned into every machine's home directory each
run and fast-forwarded, Windows included since 2026-09-05 (fixed.md), dirty
or unpushed worktrees skipped and named; archived-repo handling: root
README.md. The account holds 24: the 11 active below plus 13 archived,
uncloned.

- ansible-slb — the control plane, detailed below; absorbed the `org` repo.
- CoachLM — private life-coaching TUI agent launched through the pi entry point
  at `~/CoachLM/pi/coach` (Git Bash on Windows: `/c/Users/slb/CoachLM/pi/coach`);
  its former Python pipx app is retired.
- ProfLM — read-only CS-professor TUI agent (Python/Textual, litellm); the
  harness CoachLM was forked from.
- www — slb.dev, a Quarto site (build.ps1 renders index-gen.qmd). AWS Amplify
  app `www-slb`; publish is manual, not ansible-managed.
- www-fargo — fargo.dev, static contact card. AWS Amplify app `www-fargo`.
- fffff — C++20 Vulkan/GLFW renderer. Drives the CMake/Ninja/Clang toolchain
  and the devbox's 42128-42191/udp range, synced with the Hetzner firewall.
- local-llm-bench — local LLM benchmark harnesses, one directory per harness;
  `ollama-bench/` is the first, grading GGUF quants on the desktop's RTX 5080
  against hosted reference models. FRACTAL-only; working clone
  `D:\local-llm-bench`, which the auto-clone duplicates (fixed.md); the
  un-versioned `~/ollama-bench` scratch was folded into it and removed.
- apply_modifiers_with_shape_keys — Blender add-on forked from CGCookie's
  (GPL-3.0); external upstream, never merge it with anything.
- slbh — a Go agent harness (Bubble Tea TUI, root and child agents, streaming
  OpenAI-compatible providers, durable JSONL transcripts, managed shell jobs),
  and the owner's replacement for the pi-slb wrapper retired 2026-09-10.
  Its `quick_py` and `long_py` tools use that shared scientific environment.
  Auto-cloned like any active repo **and compiled on every target** since
  2026-09-10: `dotfiles` and `windows_dotfiles` build `./cmd/slbh` from that
  clone into `~/.local/bin/slbh` (`%USERPROFILE%\.local\bin\slbh.exe`),
  rebuilding only when the binary's embedded `vcs.revision` no longer matches
  the clone's HEAD, the clone is dirty, or the binary was built from a dirty
  tree. `windows_verify` re-checks the revision and compares `vcs.modified`
  against the clone's dirty state. It is a deployed
  application, not a managed harness: it is in no `agent_config_*` and no
  `agent_skills` entry, it configures itself through its own `/models` flow
  into `$SLBH_HOME/config.json`, and the fleet's three *managed* harnesses are
  still Claude Code, Codex and pi. Its provider keys ride the ordinary
  `api_keys` tier that was already deployed. Windows builds it too, degraded
  by the project's own account: slbh targets Linux, and the non-Linux build
  uses a shell fallback with no Linux process-group semantics.
- words — a personal values/word list, plain markdown.
- agents_old — early agent experiments, cloned everywhere (13 MB); read-only
  by convention, never restructure it.

## Fleet capabilities

Provisioned by ansible-slb on every target unless noted; operator detail in
root README.md.

### Language toolchains

Python (native python3 + pip + pipx, `ruff` as a pipx app, and a shared
per-user slbh scientific venv with pinned NumPy, SciPy, pandas, Matplotlib,
SymPy, Astropy, Skyfield, and jplephem), C/C++
(Clang/CMake/Ninja, for fffff), Node (distribution packages, Scoop
`nodejs-lts` on Windows; it is there to carry npm for pi), Deno (pinned, the
yt-dlp EJS runtime), and Go.

Go arrived 2026-09-09 and is on all five targets. The toolchain is each
target's own package — Fedora `golang`, Ubuntu/WSL `golang-go`, CachyOS `go`,
Windows Winget `GoLang.Go` — and all four are current. The two developer tools,
`gopls` and `golangci-lint`, are the exception to the native path: no
package set carries both on every target, so `go install` places them from
the pinned `go_tools` catalog in `group_vars/all/vars.yml`, into
`~/.local/bin` (`%USERPROFILE%\.local\bin` on Windows). One version of each
fleet-wide; bump the pin to move it. Why not the native packages, and why not
Scoop's golangci-lint: CLAUDE.md.

Go also compiles one owned application, slbh, from its own clone rather than
from the proxy (Repos, above). `go.mod` requires Go 1.27 and two targets'
native toolchains are older — Ubuntu/WSL 1.26.0, Fedora 1.26.8, against
CachyOS and Windows on 1.27.1 — so the build sets `GOTOOLCHAIN=auto` and Go
downloads the toolchain it needs — a 73 MB archive unpacking to 253 MB under
`~/go/pkg/mod/golang.org/toolchain@*`, once per affected host, measured on wsl
2026-09-10. That is the cost of keeping the toolchain itself on
the native package path.

### Backup

`restic` on `s3:s3.us-west-2.amazonaws.com/slb-restic`. Manual only; **agents
are barred from it**. Separately the `D:\avatars` monorepo on the desktop backs
itself up to `s3:s3.us-west-2.amazonaws.com/fargo-avatars` — distinct bucket,
IAM user and password — hence **the one backup agents may run**. Not
ansible-managed: tooling in that repo at `tools/backup/` behind a `post-commit`
hook, credentials in `~/.config/restic/avatars.env`. The restic password's
authoritative copy is in Bitwarden; rotating it without a `restic key
add`/`key remove` cycle destroys every snapshot.

That repo has **no git remote at all**, by design, so nothing should try to
audit it by upstream comparison (fleet-audit-2026-09-04.md), and WSL's Linux
git cannot read it (no `git-lfs` there) — probe it with
`git.exe -C 'D:\avatars' status -sb`. Whether a backup is owed is answered
from `%LOCALAPPDATA%\restic-avatars\backup.log`: the newest snapshot is
tagged `commit-<sha>`, and if that is HEAD, nothing is owed.

### Secrets on disk

Vault-backed `AWS_*` and LLM provider keys land in `~/.config/devbox/env`
(Linux/WSL) and the Windows user environment — the full key set is on every
machine by design. `ANTHROPIC_API_KEY` is the exception: deployed but never
exported, read from its unsourced drop box, with the managed `prof`/`proflm`
wrappers loading it for one process (CLAUDE.md names both paths and why).

### Agents

Three managed harnesses, all unsandboxed and reconverged every run: **Claude
Code**, **Codex** and **pi**. Any of the three can hold the control session;
all three are worker harnesses, through their own native subagents. The
control session gets the control-session instructions, every worker the
shorter worker set. The binding contract is agent-harnesses.md; operational
caveats and evidence links are agents.md.

Three routing rulings, all the owner's, all 2026-09-05 (models.md):

- pi runs GLM 5.3 Flash on the Z.ai GLM Coding Plan by default
  (`ZAI_API_KEY`, plan-billed, pinned to `api.z.ai`).
- On OpenRouter, GLM 5.3 Flash is **the only model approved to run — no other
  is cheap enough** (`z-ai/glm-5.3-flash`).
- **A model reachable on a plan never runs through OpenRouter, and every plan
  model runs through its native harness**: GPT-6 and GPT-5.6 through Codex
  only, every Claude model through Claude Code only.

Every model the fleet uses, and where each is the default: models.md.

Sessions do not coordinate; one started over Windows sshd is elevated and
SendMessage-unreachable from a desktop session, so the `inbox` skill is the
floor under cross-session, cross-machine and cross-harness messaging. A worker
is reachable through the harness that spawned it and nothing else.

### Worker runtime — retired 2026-09-10

There is no fleet worker runtime. pi-slb, the `agent-supervisor`, the
`pi-run`/`codex-run`/`claude-run`/`z-run` wrappers, `agent-run`, `agent-msg`,
the four `~/.local/bin` shims and every `~/.agent-runs` tree were retired on
the owner's ruling and removed from every host. **Do not rebuild it, and read
any page describing it as history.**

Delegation is each harness's own subagent mechanism: Claude Code's `Agent`
tool, Codex's `spawn_agent` against the `worker` role, pi's own subagents. A
worker is reachable from the session that spawned it and from nowhere else;
`inbox` remains the floor under everything cross-machine.

What the runtime measured across 828 runs on four hosts, and where each
conclusion it produced now lives: agent-runs-sweep-2026-09-10.md. Its design
and its acceptance pass are worker-runtime-plan-2026-09-03.md and
worker-runtime-acceptance-2026-09-04.md; the pi-slb pages are indexed as
retired in deeper-docs.md. Nothing was kept out of it. pi's compaction
extension was briefly carried over and then withdrawn the same day on the
owner's ruling, so pi runs its stock compaction under the managed `compaction`
settings block (compaction-2026-09-09.md is what the extension was for, and is
history).

### Agent skills

Eleven, listed in `agent_skills`, copied verbatim into `~/.claude/skills` and
`~/.agents/skills`, each root pruned to exactly that list: `org` (this map),
`downloader`, `vrchat-avatars`, `inbox`, `close-up-shop`, plus the six Runpod
skills vendored 2026-09-07 (`runpod`, `runpod-mcp`, `runpodctl`, `flash`,
`runpod-usage`, `companion-clis`; the hosted MCP server for pi and Codex is in
the managed config sources, and the `runpod@runpod` Claude Code plugin is
hand-installed on the controller host only, like `codex login` — owner OAuth
per host, never copied). Deployed files are mode 0600, so a script runs as
`bash <path>`, never directly. It was seventeen until 2026-09-10; the six that
left were the worker runtime's.

Which harness sees which is policy, not deployment, and is canonical in
agent-harnesses.md: a control session sees all eleven; a worker sees all but
`close-up-shop`. Evidence: skills-policy-plan-2026-09-03.md, written when the
list was longer and the five launch entrypoints were the thing being hidden.

Pruning is whole-skill only. A file dropped from a skill that survives needs
its path in `agent_skill_purge_paths`, a withdrawn `~/.local/bin` shim needs
its name in `agent_bin_shims_retired`, and both are asserted absent by
`windows_verify` — the only check in either that can fail. Root `README.md`
has the mechanics.

### Local LLM runtime

Ollama on Linux targets serves on the default `127.0.0.1:11434`; the Windows
desktop's local RTX 5080 provider serves on its current Tailscale interface at
port 11434, with the inbound rule scoped to that interface. Models on the
desktop live at `D:\ollama\models` and none are ansible-managed. Linux targets
run it as a systemd unit. Windows keeps the GUI tray app Startup shortcut for
the interactive session, while `windows_tailscale` also manages a SYSTEM
scheduled task that launches `ollama.exe serve` with the managed environment,
so the tailnet listener survives WinRM session teardown and reboots.
`slbh` exposes the campaign workhorse as `local/q27-IQ2_M-96k`, the default
leaf model. The route was verified from devbox over `tailscale0` with a live
`/v1/models` response containing `q27-IQ2_M-96k:latest`; `/api/ps` was empty
after the check. Verify the GPU with a real load reporting a processor split
and a throughput on the known curve, never with a version — a broken upgrade
serves every model on the CPU silently: ollama-cuda-repair-2026-09-04.md.

On the desktop the server can be found running elevated in session 0
(local-quants-2026-09-05.md): the user cannot stop it, and
`ansible winbox -i inventory.ini -m ansible.windows.win_shell -a 'taskkill /F /PID <pid>'`
over the elevated WinRM transport is what does. **Unload Ollama
(`keep_alive: 0`, about two seconds) before running any direct `llama-server`
probe** — the two share an image name and nothing in the process list
separates them, so it is a standing rule and not a bug to fix (fixed.md).

Quant benchmarking lives in the `local-llm-bench` repo; the v5 suite's bands
and the fair-weather resident-size threshold are in
local-llm-bench-desaturation-2026-09-05.md. **Ruling (amended 2026-09-06): two
quant roles, each with its own floor.** The long-context quant is viable only
if it runs 48k context with no degradation (resident under the line and gen
tok/s on its curve); 64k is better. The short-context quality quant is viable
only if it runs 24k with no degradation and a measured margin under the
fair-weather line; it may run higher where it fits. A quant that fits neither role is a candidate for removal.
Q3_K_M and Q3_K_L were removed under the original 48k-only ruling. The roles
and the chosen quants: local-workhorse-plan-2026-09-06.md. The scored roster,
each quant's placement and the v7 rung: local-quants-2026-09-05.md.

### Sync

A procedure, not a tool: the git rules in every agent's instructions
(`agent_config_instructions`); nothing sweeps. **Never use ansible
playbooks for a sync.**

### Codex login

One-time `codex login` per host (ChatGPT plan, not an API key); `auth.json` is
never copied between machines and `CODEX_API_KEY` is never deployed, both for
reasons CLAUDE.md gives. Every live host has a login, devbox included
(wrt-trial-2026-09-05.md). The by-hand Windows update path and the upstream
bug: agents.md.

## Roles

Two standing roles; a task names the one it means. They used to be four, and
the other two — the project manager and the auditor-intern — were positions in
the pi-slb runtime, which was retired on 2026-09-10 along with its five
internal role names (`control`, `overseer`, `manager`, `worker`, `reviewer`).

A **control session** delegates well-defined work, verifies what comes back,
and commits, and keeps *both* ends busy: it never blocks waiting on a worker,
and never leaves one idle either (subagents-2026-09-04.md). When a call is
genuinely the owner's, bank it and carry on: **banking stops a decision, not
the work**. It closes shop alone through the `close-up-shop` skill; no worker,
reviewer or audit run takes part (closing-audit-2026-09-04.md). **Control
sessions run in WSL only**, where the controller clone and the skill roots are
local and every fleet action is native; a resident WSL session also keeps the
VM, and every background run under it, alive. Any of the three managed
harnesses may hold the seat. A Claude Code session on Windows is a
**workstation session**: it works the `D:\avatars` monorepo and the desktop
apps, runs that repo's own backup hook, and never converges, closes shop or
commits for the fleet.

A **worker** — Luna (`gpt-5.6-luna`), the default for every delegated task and
for web research — does that delegated work and reports back to the session
that asked for it, and is a subagent of that session's own harness: Claude
Code's `Agent` tool, Codex's `spawn_agent` against the `worker` role, pi's own
subagents. There is no fleet launcher any more. The ChatGPT plan is Luna's;
when a run reports a quota refusal the session stops sending Codex work and
says so, and the owner resets the plan. Luna is not rationed and concurrency
needs no justification (owner, 2026-09-09). An Opus subagent is the fallback,
for work that needs Claude Code's own tools or when Luna has come back wrong.
GLM 5.3 Flash through pi, or local Ollama, is the third choice when neither
family fits, including a review of Luna's own work; verify what it returns.
Workers think at `high` (owner, 2026-09-08).
GPT-6 Astra is retired from use: it is not run on any harness and is not
proposed, and no pin names it. The plan cost that argues against it is
measured in astra-control-trial-2026-09-05.md. Luna is the Codex default on
both sides — the ChatGPT seat's own TUI model and the spawned-worker
default — so the seat and its workers share one model.
A review never goes to the author's own model family: Luna reviews
Claude-authored plans and code, and GLM reviews Luna's work by default;
whether a change is reviewed at all is the control session's judgment, never a
mandate.

The instruction variables and their deployment paths are canonical in
`CLAUDE.md`, not restated here.

## Control plane: ansible-slb

To change any machine — packages, services, firewall, dotfiles, agent config —
edit ansible-slb and run the target's playbook. **Never configure hosts by
hand.** One playbook per target, deliberately no `site.yml` (CLAUDE.md).

- **The WSL clone `~/ansible-slb` inside Ubuntu is the only controller** — if
  your working directory is not `/home/slb/ansible-slb`, you are in the wrong
  one. The copy at `C:\Users\slb\ansible-slb` cannot run a play at all
  (CLAUDE.md).
- **The two clones drift both ways, and `./win.sh` runs whatever the WSL clone
  has**: editing the Windows copy converges the *old* code and reports success
  (CLAUDE.md). Changes reach a play only via commit → push → pull in WSL;
  verify the new tasks ran, not the recap.
- **`org/**` is the one carve-out**: markdown, no play reads it, so this map
  may be edited from either clone — still commit, push and pull in WSL before
  any play.
- Driving the WSL controller from a Windows session has three traps (VM
  shutdown, boot-wiped `/tmp`, Git Bash path rewriting), so anything
  non-trivial goes in a script file run with
  `MSYS_NO_PATHCONV=1 wsl.exe -- bash /mnt/c/…/script.sh`:
  windows-play-profile-2026-09-02.md.
- Everything else — role ordering, tags, lint gates, agent-config variables,
  the Windows per-task floor — is canonical in root README.md and
  CLAUDE.md/AGENTS.md. Baselines: converge-performance-2026-09-03.md.

## Conventions

- git: branch main everywhere; SSH-signed commits as slb <mail@slb.dev>;
  commit messages 1-5 words, lowercase, one line; agents never add themselves
  as contributors.
- Python apps are editable pipx installs; no virtualenv juggling by hand.
- Evidence: a number is a measurement only if it came from the thing it
  describes, on the arm that will run it. What was *written* is not what
  *arrived*, and a stand-in model does not size the real one:
  subagents-2026-09-04.md.
- Plans handed to an autonomous session name what that session may decide, and
  keep the owner's list short and explicit. A gate only the owner can open
  stops the whole run when it is reached, however clearly the plan also says to
  carry on around it. Either write the gate out of the plan or write down what
  to do while it stands: subagents-2026-09-04.md.
- Keep this map in sync: any change to machines, services or repos updates
  `org/README.md` in the same commit as the infra change. One repository, one
  commit — a converge and its description ship together.
- Root `README.md` and `CLAUDE.md` are canonical for anything they state; do
  not restate them here or in `org/agents.md`. `org/<topic>.md` is a
  current-state page;
  `org/<topic>-YYYY-MM-DD.md` is evidence, written once and extended only by a
  dated addendum. Run `python3 scripts/validate-org-docs.py` with `ansible-lint`
  before committing anything under `org/`.

## Deeper docs

Every dated page and topic page not named above is indexed, one line each
with what it holds, in `deeper-docs.md`; `agents.md` is the harness page.
Open the index when a claim in this map points at a dated file; never
re-derive a measurement one of those pages already holds.
