# Local Ollama route, 2026-09-11

The local RTX 5080 route is live and managed. `slbh` exposes the tested
workhorse as `local/q27-IQ2_M-96k`, sends the wire model name
`q27-IQ2_M-96k` without an API key, and uses the desktop Ollama endpoint at
`http://fractal.wyvern-temperature.ts.net:11434/v1/chat/completions`.

## Evidence

The checks below were run from the WSL controller and from devbox after the
fleet converge:

- `fractal.wyvern-temperature.ts.net` resolved on devbox to
  `100.x.x.x`.
- `tailscale ping fractal` returned pong in 40 ms.
- `ip route get 100.x.x.x` on devbox selected `dev tailscale0` with
  source `100.x.x.x`.
- A devbox-originated request to `/v1/models` returned
  `q27-IQ2_M-96k:latest`.
- `/api/show` for `q27-IQ2_M-96k` returned the existing model with
  `num_ctx 98304` and the IQ2_M quantization metadata.
- `/api/ps` was empty after the checks, so the verification did not leave the
  workhorse resident on the card.

## Managed boundary

Windows binds `OLLAMA_HOST` to the current Tailscale IPv4 address at port
11434. `windows_tailscale` owns an inbound TCP firewall allow rule scoped to
the Tailscale interface, never to a fixed `100.x` address. A SYSTEM scheduled
task runs a generated environment wrapper for `ollama.exe serve`, so the
listener survives WinRM session teardown and reboot. The GUI tray-app Startup
shortcut remains for the interactive desktop session.

The route and server boundary are Ansible-managed; Ollama model blobs remain
outside Ansible. The model approval and leaf default remain in slbh's own
`$SLBH_HOME/config.json`, not in the managed harness configuration.

## Scope

This closes the endpoint/provider integration and the default-leaf wiring. The
local-workhorse plan's later availability signal, external queue, accounting
ledger, shadow comparisons and review lane are not claimed complete by this
route check.
