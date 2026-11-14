# Raspberry Pi 5

**Experimental:** No launch, casting, playback or TV audio test has been run on this board. AppArmor may [block portable Electron](../../docs/compatibility.md#electron-sandbox-startup) on Ubuntu 24.04.

## What to buy

Choose **4GB or more** for the documented Ubuntu 24.04 Desktop path. Lower-memory
Pi 5 variants are not a supported shortcut for this setup. Additional RAM may
help when sharing the host, but no JetsonCast performance minimum has been measured.

Budget for a suitable power supply, cooling, a case, a micro-HDMI cable, and
storage (32GB or larger recommended). Use the board-specific Ubuntu image;
Raspberry Pi OS and Ubuntu 26.04 are outside the current installer targets.
[Official Pi 5 setup guidance](https://www.raspberrypi.com/documentation/computers/getting-started.html).

## Set up

1. Use the Pi-specific Ubuntu 24.04 LTS Desktop ARM64 image and a Pi 5 with at least 4 GB of RAM. Ubuntu's [board support matrix](https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/#supported-models) does not list 22.04 for the Pi 5. A generic ARM image or 32-bit Raspberry Pi OS is outside this setup path.
2. Connect micro-HDMI to your TV. Start with one display and check both picture and audio in Ubuntu. Use the board's recommended power supply and cooling.
3. From the checkout, run `python3 install.py --device raspberry-pi-5`. Then [launch and cast](../README.md#set-up-the-computer-connected-to-your-tv). Start with 720p and verify fullscreen, sound and return to idle before increasing quality. Do not assume hardware decoding or 4K playback.

Preview without installing: `python3 install.py --device raspberry-pi-5 --dry-run --non-interactive`.
If Electron is blocked by the sandbox policy, stop at the compatibility guide;
do not use `--no-sandbox` or disable system-wide protections to force it to run.

## Sharing with Pi-hole

Both services can share a suitable Ubuntu host, but Pi 5 coexistence and playback
are not yet validated. Preserve the existing Pi-hole installation, network
settings and DNS address, and test DNS under video load. [Coexistence guide](../../docs/pi-hole.md).
