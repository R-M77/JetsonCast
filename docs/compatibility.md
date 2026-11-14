# Compatibility

## Electron sandbox startup

Ubuntu 24.04 restricts unprivileged user namespaces through AppArmor. Some
portable Electron builds may fail to launch without an administrator-approved,
application-specific profile. Jetson Cast does not modify AppArmor, set SUID
permissions, disable system protections or add `--no-sandbox`. If you encounter
a sandbox startup error, stop and consult your distribution's policy; do not
disable protections system-wide. This package's Ubuntu 24.04 runtime path is
not yet verified. [Ubuntu release notes](https://documentation.ubuntu.com/release-notes/24.04/#unprivileged-user-namespace-restrictions).

The upstream renderer itself has reduced isolation; see [Security](../SECURITY.md).

## Host and display

This table describes the **standard edition**. The opt-in
[Pi Lite experiment](../experiments/pi-lite/) has a separate Raspberry Pi OS
ARM64 path for Pi 3 / Zero 2 W; no physical playback or audio validation yet.

| Component | What to use | Verification |
| --- | --- | --- |
| Operating system | 64-bit Ubuntu 22.04 or 24.04 LTS with a graphical desktop and Python 3.10+ | Physical TV integration on Ubuntu 22.04 with a Jetson Orin Nano 8 GB. Ubuntu 24.04 startup is unverified. |
| CPU | ARM64 (`aarch64`) or x86-64 (`amd64`) | The x86-64 release download, extraction and patch were checked; physical x86-64 playback remains untested. Raspberry Pi 4/5 and other ARM64 boards are experimental. |
| Desktop | X11 for the tested path | Wayland fullscreen, idle behavior and display wake can vary by compositor. |
| Video and audio | HDMI or DisplayPort with audio routed to the TV or sound system | Check the active audio output during setup. Resolution, codec support, and hardware decoding depend on the computer, drivers, and display. |
| Network | Phone and receiver on the same trusted LAN, with internet access for installation and YouTube | DIAL discovery needs a LAN that allows devices to reach each other. |

See the [device guides](../devices/) for display connections, board-specific Ubuntu requirements and the exact level of verification. Windows, macOS, 32-bit systems and headless playback are outside these setup paths.

`python3 install.py doctor` reports the detected device profile, desktop session and available audio controls. `python3 install.py --dry-run --non-interactive` previews setup without downloading. During installation, `ldd` checks the verified VacuumTube executable for missing desktop libraries before the app is installed. A dependency check cannot verify startup, display output or playback. See [missing libraries](#missing-desktop-libraries) for package names. `ldd` comes from `libc-bin`; `pactl` is optional and comes from `pulseaudio-utils`. Without `pactl`, select the TV output using Ubuntu's Sound settings.

Open an on-screen terminal for interactive setup. For remote provisioning, `python3 install.py --non-interactive` uses the default settings; launch the receiver later from the graphical desktop. Optional login autostart launches the receiver after a graphical sign-in. The installer runs without administrator rights. It leaves system sign-in, router, DNS and firewall settings alone.

## Manage your installation

Run these commands from the cloned repository:

| Task | Command |
| --- | --- |
| Change name, TV audio or login startup | `python3 install.py configure` |
| Check the host and installation | `python3 install.py doctor` |
| List the device guides | `python3 install.py devices` |
| Preview installation without downloading or writing files | `python3 install.py --dry-run --non-interactive` |
| Remove the app and launchers, keeping the private profile and settings | `python3 install.py uninstall` |

## Missing desktop libraries

Install the package that matches the missing library and your Ubuntu release using your normal Ubuntu package manager, then rerun setup. System package installation may require your desktop administrator. These common mappings come from Ubuntu's package index; setup does not install system packages automatically.

| Missing library | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| --- | --- | --- |
| `libgtk-3.so.0` | [`libgtk-3-0`](https://packages.ubuntu.com/uk/jammy/arm64/libgtk-3-0/filelist) | [`libgtk-3-0t64`](https://packages.ubuntu.com/en/noble/amd64/libgtk-3-0t64/filelist) |
| `libasound.so.2` | [`libasound2`](https://packages.ubuntu.com/jammy/amd64/libasound2/filelist) | [`libasound2t64`](https://packages.ubuntu.com/eu/noble-updates/amd64/libasound2t64/filelist) |
| `libnss3.so` | [`libnss3`](https://packages.ubuntu.com/jammy/amd64/libnss3/filelist) | [`libnss3`](https://packages.ubuntu.com/noble/libnss3) |
| `libgbm.so.1` | [`libgbm1`](https://packages.ubuntu.com/jammy-updates/libgbm1) | [`libgbm1`](https://packages.ubuntu.com/noble/amd64/libgbm1/filelist) |

Use the package for your native architecture: `amd64` on Intel/AMD or `arm64` on the listed ARM boards. Installing the libraries does not establish Ubuntu 24.04 sandbox compatibility; its Electron startup path remains unverified.

## Casting and HDMI inputs

The YouTube app discovers Jetson Cast using VacuumTube's DIAL support. The Linux computer plays the video and the phone controls it. This is an unofficial receiver for YouTube. Prime Video, Netflix, Plex, other Google Cast apps, and screen mirroring are outside its scope. [VacuumTube discovery settings](https://github.com/shy1132/VacuumTube/blob/v2.0.1/README.md#settings)

An existing Chromecast can continue to handle its supported apps on a separate TV input. Use the TV's input selector to return to the Linux computer. A separately configured, experimental helper can switch back to the Jetson Cast input on certain older Samsung TVs. Model, firmware, and network behavior determine whether it works. Use the YouTube app for playback controls. TV remote play and pause over HDMI-CEC are unverified.

The helper can select either receiver's input and pause the other player.
It requires device-specific configuration; see [optional setup](../addons/README.md).

## Appliance-style startup

Choose login autostart during setup to reopen the receiver after a desktop
sign-in. To skip sign-in entirely on a dedicated TV computer, configure
automatic login yourself in Ubuntu's Users settings for a dedicated account.
Anyone with physical access will then be able to use that account. The
installer deliberately does not change login security or request passwords.
Keep the TV powered and on the expected input when testing cold boots.

## Ads and optional DNS filtering

VacuumTube provides YouTube ad blocking. Its effectiveness can change as YouTube changes. SponsorBlock is a separate, optional feature based on community submissions. [VacuumTube settings](https://github.com/shy1132/VacuumTube/blob/v2.0.1/README.md#settings)

Pi-hole is a separate optional service. It filters by domain, so when an ad and the video use the same domain, as can happen with YouTube or Prime Video, DNS filtering cannot reliably remove just the ad. [Pi-hole documentation](https://docs.pi-hole.net/) · [Pi-hole discussion of same-domain YouTube ads](https://discourse.pi-hole.net/t/pihole-as-a-server-and-is-not-stopping-youtube-ads/74590)

Sharing the TV computer with Pi-hole? See the [coexistence guide](pi-hole.md)
for memory, service isolation and DNS availability considerations.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Jetson Cast is missing from the Cast menu | Open Jetson Cast on the computer. In its window, press `Ctrl+O` and check **Device Discoverability**. Verify that the YouTube app has local network access if prompted. Check whether guest Wi-Fi or client isolation prevents the devices from communicating. |
| Video plays without TV sound | Confirm the TV is on the correct input and unmuted. Check the Ubuntu sound settings for the active HDMI or DisplayPort output. Run `python3 install.py configure` from the checkout to revisit setup choices. |
| Fullscreen or idle artwork behaves unexpectedly | Try an X11 desktop session, where available. Use `python3 install.py doctor` from the checkout to check the installation. |
| Setup reports missing desktop libraries | Use a full Ubuntu desktop for your device. Ask your desktop administrator to install the packages that provide the library names shown by setup. |
| Video stutters | Lower the playback quality and retest. High resolutions and hardware decoding depend on the device and codec. |

[Back to quick start](../README.md#quick-start) · [Network and security](../SECURITY.md)
