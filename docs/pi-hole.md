# JetsonCast alongside Pi-hole

**Yes: both can share a capable Ubuntu computer.** Coexistence was observed on
the project's Jetson Orin Nano 8GB development setup. It is not yet benchmarked
on Raspberry Pi 4/5 or other hardware.

| Service | Job |
| --- | --- |
| JetsonCast / VacuumTube | YouTube playback and application-level ad blocking on the TV; needs a graphical desktop. |
| Pi-hole | DNS filtering for clients configured to use it; runs independently of the desktop session. |

Pi-hole is optional and separate. JetsonCast does not install, manage or replace
it. Pi-hole's domain filtering does not reliably remove YouTube ads served
from the same domains as the videos. The TV ad-blocking feature comes from
VacuumTube. [Pi-hole's same-domain explanation](https://discourse.pi-hole.net/t/pihole-as-a-server-and-is-not-stopping-youtube-ads/74590).

## If Pi-hole already works

1. Check the host is a supported **64-bit Ubuntu desktop** with working TV
   picture and audio. A headless Pi-hole server or Raspberry Pi OS installation
   is not automatically a JetsonCast host. Do not reimage a working DNS server
   to try this project; a separate TV computer is often simpler.
2. Keep Pi-hole's address, DNS/DHCP settings, ports, service/container and data
   unchanged. Preview JetsonCast with `python3 install.py --dry-run --non-interactive`,
   then follow the normal setup from the desktop. The installer changes only
   its user-owned app files; it does not restart Docker or alter DNS/router/firewall settings.
3. Test one phone cast while another existing Pi-hole client browses normally.
   Confirm Pi-hole is still resolving queries and watch for memory pressure,
   swapping, heat or throttling during playback and animated idle mode.

For a new shared host, **4GB RAM or more is a practical starting recommendation**,
not a measured guarantee. Pi 4 2GB may fit the Ubuntu 22.04 desktop requirements,
but shared-service performance has not been validated. Pi 5's documented
Ubuntu 24.04 Desktop path requires at least 4GB and still has an unverified
Electron startup path. See [Pi 4](../devices/raspberry-pi-4/) / [Pi 5](../devices/raspberry-pi-5/).

## Keep DNS available

The [Pi Lite experiment](../experiments/pi-lite/) is not validated alongside
Pi-hole. Keep DNS on an existing stable host while testing these low-memory boards.

Closing JetsonCast should not stop Pi-hole. Suspending, powering off or rebooting
their shared computer stops both; DNS clients can lose name resolution while
it is unavailable. Keep that host awake when clients depend on it and plan
maintenance accordingly. Turning off only the TV is different from powering
off the computer. Autologin is not required for Pi-hole.

Pi-hole uses DNS port 53 plus its configured web/service ports. Review actual
listeners before adding services; do not disable a working DNS service to
resolve a conflict. Existing standalone and Docker Pi-hole deployments need
no migration just to try JetsonCast. [Official requirements and ports](https://docs.pi-hole.net/main/prerequisites/).

No Pi-hole credentials, client lists, queries, LAN addresses, or real deployment
configuration belong in the repository. This guide intentionally contains no
ready-to-run router changes or personal configuration.
