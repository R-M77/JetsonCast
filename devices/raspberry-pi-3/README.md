# Raspberry Pi 3

**Experimental Lite route; no physical validation.** Pi 3 B/B+ have
64-bit CPUs but only **1GB RAM**. Their ability to run Linux or Pi-hole does
not establish enough memory for the standard edition's Ubuntu desktop, Electron player and
animated screensavers. [Official board specifications](https://www.raspberrypi.com/documentation/computers/sbcs.html).

The standard Ubuntu paths start at Pi 4 with 2GB on 22.04, or supported 4GB
boards on 24.04. [Ubuntu board matrix](https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/).

The separate [Lite experiment](../../experiments/pi-lite/) now targets
Raspberry Pi OS 64-bit on Pi 3 using `--lite`. It keeps the casting/ad-blocking
engine, enables upstream low-memory mode and omits GIFs, Jet and the optional
input helper. Pi 3 B/B+ is the first test target; Pi 3 A+ has only 512MB and
faces the same memory uncertainty as Zero 2 W. No sustained playback or audio
result is available. Adding swap does not establish support.

Keep an existing Pi-hole working on its current machine and use a different
computer for TV playback. See [Pi-hole coexistence](../../docs/pi-hole.md) and
the [hardware shortlist](../buying.md).
