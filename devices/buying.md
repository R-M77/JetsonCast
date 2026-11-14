# Pick hardware for your TV

Start with a computer you already own. These are setup candidates, not a list
of certified purchases. Only Jetson Orin Nano 8GB with Ubuntu 22.04/X11 has
physical JetsonCast casting, playback and sound confirmation.

| Priority | Candidate | What to check |
| --- | --- | --- |
| Lowest additional cost | Existing compatible Ubuntu laptop/desktop | TV picture and audio work before installing. |
| Budget used computer | [Dell Wyse 5070](dell-wyse-5070/) | Working storage, power supply, Wi-Fi if needed, and DisplayPort-to-HDMI audio. |
| Small board you already have | [Pi 4](raspberry-pi-4/) | 2GB with Ubuntu 22.04 is a candidate; 4GB offers more headroom. Both are untested here. |
| Newer common board | [Pi 5](raspberry-pi-5/) | 4GB+, Ubuntu 24.04; sandbox startup and playback remain unverified. |
| Tiny complete PC | [GMKtec NucBox G5](gmktec-nucbox-g5/) or a comparable Intel N97/N100/N150 mini PC | Ubuntu drivers, native HDMI audio, cooling, return policy and actual total cost. |

Compare complete systems: board/PC, RAM, storage, power supply, case/cooling,
Wi-Fi and TV cable. A cheap bare board can cost more than a used PC once equipped.
Prefer a returnable purchase until discovery, fullscreen playback, TV sound,
idle artwork, and a second cast have been tested on that exact device.

## Can I go cheaper than a Pi 4?

- **Pi 4 2GB:** the lowest-memory candidate for the standard Ubuntu edition,
  using Ubuntu 22.04 Desktop. It is not a proven minimum or a 1080p guarantee.
- **[Pi Zero 2 W](raspberry-pi-zero-2-w/) and [Pi 3](raspberry-pi-3/):** outside
  the standard Ubuntu path. An opt-in [Lite experiment](../experiments/pi-lite/)
  now targets Raspberry Pi OS with less overhead, but has no physical playback
  evidence. Try it on a board you already own; do not buy one expecting success.
- **Pi 4 1GB / Pi 5 below 4GB:** outside the desktop requirements for their
  documented setup paths. Do not confuse an OS booting with smooth video playback.
- **[NanoPi](nanopi/):** check the exact board; some are headless routers.
- **[ESP32 / Pico](esp32/):** cannot host the current application.

For a combined TV receiver and DNS server, see [Pi-hole coexistence](../docs/pi-hole.md).
Hardware facts and upstream requirements were checked on 2026-11-10; prices
are deliberately omitted because they vary by seller, accessories and region.
