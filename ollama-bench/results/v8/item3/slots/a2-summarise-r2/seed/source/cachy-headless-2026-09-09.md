# Cachy headless decision — 2026-09-09

## Decision

CachyOS (`cachyos-x8664`) is now a headless target. The play stops
provisioning GUI packages and declares `multi-user.target` as the systemd
default target while disabling `plasmalogin.service`. The role does not stop a
running graphical session; a later reboot is required for the declared boot
posture to take effect.

The GTX 1080 Ti capacity analysis in
[`cachy-1080ti-options-2026-09-08.md`](cachy-1080ti-options-2026-09-08.md)
showed that the extra VRAM margin matters for local model serving. This page
records the separate live-host evidence for retiring the idle graphical
stack.

## Read-only measurement

These figures were measured read-only from the live host by the control seat
on 2026-09-09. The host has a GTX 1080 Ti with 11,264 MiB total VRAM and was
using 1,100 MiB at idle:

| Process | VRAM |
| --- | ---: |
| `plasma-login-wallpaper` | 232 MiB |
| `plasma-login-greeter` | 175 MiB |
| `kwin_wayland` (greeter's) | 32 MiB |
| `kwin_wayland` (user session) | 269 MiB |
| `firefox` | 137 MiB |
| `plasmashell` + `Xwayland` + `kscreenlocker_greet` | 8 MiB |
| `deno` — the downloader's PO-token provider | 2 MiB |
| Unattributed driver/framebuffer | ~249 MiB |

The graphical stack accounts for 851 MiB. Of that, 439 MiB is the login
greeter and wallpaper, which nobody is looking at on an unattended box. RAM
was 15,895 MiB, with 2,016 MiB of swap in use despite 9.3 GiB free.

The live display manager was `plasmalogin.service`, enabled and running since
2026-09-06; it was not sddm, gdm, lightdm, greetd, or ly. The live default was
`graphical.target`.

## Scope

Scope A, stopping GUI provisioning, and scope B, headless boot posture, were
approved. Scope C, removing installed desktop packages with `pacman -Rs`, was
considered and explicitly refused. This change adds no package removals and
does not touch `plasma-desktop` or `cachyos-kde-settings`.

Firefox remains installed. Because its CachyOS role is retired, the existing
`/etc/firefox/policies/policies.json` will remain deployed and unmanaged on
the host as one accepted inert file. No purge mechanism is added.

## Declared state and reboot

The `cachyos_headless` role reads `systemctl get-default` and runs
`systemctl set-default multi-user.target` only when the current value differs.
It stats the known unit path before inspecting `systemctl is-enabled`, so an
absent `plasmalogin.service` is harmless. If the unit exists and is enabled,
`systemd_service` declares `enabled: false`; no task uses `state: stopped` or
`--now`.

`systemctl set-default` changes the default-target symlink for the next boot,
and disabling `plasmalogin.service` prevents the display manager from being
started as part of that next boot. Neither operation ends the current Plasma
session. The existing `cachyos_reboot` role only detects a missing running
kernel module directory, so it will not notice this posture change. No reboot
trigger was added: the owner must arrange a later reboot, after which the
declaration becomes effective.
