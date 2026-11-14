# Raspberry Pi Zero / Zero 2 W

**Experimental Lite route; no physical validation. Do not buy one for it yet.**

An opt-in [Lite edition](../../experiments/pi-lite/) targets Raspberry Pi OS
64-bit on Zero 2 W. It enables upstream low-memory mode, omits animated
screensavers and Jet, and retains the YouTube-app casting/ad-blocking engine.
It still needs Electron; 512MB may not be enough for stable playback.
Use `--lite` only on a spare test card. The standard Ubuntu path is unchanged.

Zero 2 W has a 64-bit Cortex-A53 CPU but only **512MB RAM**. Its small size and
advertised H.264 decoding do not establish that a full Electron/YouTube desktop
application will run acceptably. Original Zero/Zero W models also have a 32-bit
CPU, incompatible with the provided ARM64 binary. [Official Zero specifications](https://www.raspberrypi.com/documentation/computers/zero.html).

The documented Ubuntu desktop paths require at least 2GB for Pi 4 on 22.04,
or 4GB for the 24.04 desktop targets. Zero 2 W is not a standard installer profile.
[Canonical's board matrix](https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/).

An existing Zero may still be useful for a separate lightweight service such
as Pi-hole if its OS and resources meet that service's requirements. That does
not make it a JetsonCast host. [Pi-hole prerequisites](https://docs.pi-hole.net/main/prerequisites/).
For the standard Ubuntu edition, see [Pi 4 2GB with Ubuntu 22.04](../raspberry-pi-4/).
