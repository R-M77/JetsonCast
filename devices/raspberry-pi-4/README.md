# Raspberry Pi 4 Model B

**Experimental:** The project has not tested launch, casting, playback or TV audio on this board. Jetson's ARM64 results do not establish Pi graphics or decoding performance.

## Choose the memory size

| Pi 4 RAM | Current setup path |
| --- | --- |
| 1GB | Outside the documented Ubuntu desktop requirements; do not buy it for this package. |
| 2GB | Lowest-memory candidate: Ubuntu 22.04 Desktop ARM64 only. Performance is unverified. |
| 4GB or 8GB | More headroom for desktop playback and other services; still experimental. Ubuntu 24.04 needs at least 4GB. |

For a new purchase, 4GB is our practical starting recommendation, not a measured
JetsonCast minimum. A used board can be better value than a new kit. Include a
reliable microSD card (32GB or larger recommended), power supply, case/cooling,
and micro-HDMI-to-HDMI cable in the total. The board is about 85 × 56 mm before
its enclosure. [Raspberry Pi hardware reference](https://www.raspberrypi.com/documentation/computers/sbcs.html).

## Set up

1. Use a 64-bit Ubuntu Desktop image for the Pi 4 Model B. Canonical lists desktop support for 22.04 on boards with at least 2 GB of RAM and for 24.04 with at least 4 GB. These are [Ubuntu's desktop minimums](https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/#supported-models), not Jetson Cast performance targets. Ubuntu 24.04 may [block portable Electron](../../docs/compatibility.md#electron-sandbox-startup).
2. Connect micro-HDMI to the TV, select the input, and verify that Ubuntu displays and sends sound to the TV. Use the board's recommended power supply.
3. From the checkout, run `python3 install.py --device raspberry-pi-4`. Then [launch and cast](../README.md#quick-start). Test short videos at 720p before trying 1080p. Check idle and resumed playback as well as sound; hardware decoding is unverified.

Preview without installing: `python3 install.py --device raspberry-pi-4 --dry-run --non-interactive`.
Raspberry Pi OS is not supported by the current installer, even when it is 64-bit.
Do not reimage a working DNS server just to follow this guide.

## Sharing with Pi-hole

A Pi 4 is a candidate for both services on a compatible Ubuntu desktop; this
combination has not been load-tested on a Pi. Start with 4GB or more if buying
for both, and check DNS responsiveness during playback. Keep Pi-hole running
independently of the graphical login. [Coexistence guide](../../docs/pi-hole.md).
