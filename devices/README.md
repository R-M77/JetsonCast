# Set up the computer connected to your TV

Jetson Cast runs on a Linux computer connected to the TV by HDMI or DisplayPort. Your TV only needs an input that works with your computer or adapter. The phone runs the YouTube app; the computer handles playback and TV audio. Nothing is installed on the TV.

| Computer | Ubuntu desktop | Jetson Cast verification |
| --- | --- | --- |
| [NVIDIA Jetson Orin Nano](jetson-orin-nano/) | 22.04 is the tested setup | Physical casting, fullscreen playback and sound on the 8 GB model with X11 |
| [Intel or AMD mini PC](mini-pc/) | 22.04 or 24.04, x86-64 | Archive verified and patched; no physical playback test |
| [Dell Wyse 5070](dell-wyse-5070/) / [GMKtec NucBox G5](gmktec-nucbox-g5/) | Same x86-64 setup | Specific buying/setup guides; neither model physically tested |
| [Repurposed Intel or AMD laptop or desktop](x86-pc/) | 22.04 or 24.04, x86-64 | Same archive checks; no physical playback test |
| [Raspberry Pi 4 Model B](raspberry-pi-4/) | 22.04 or 24.04, ARM64 | Experimental |
| [Raspberry Pi 5](raspberry-pi-5/) | 24.04, ARM64 | Experimental |
| [Other ARM64 computer](generic-arm64/) | Board-supported 22.04 or 24.04 desktop | Experimental |

The same installer serves every guide. Ubuntu 24.04 startup and Wayland playback are [unverified](../docs/compatibility.md), including on previously tested hardware. Windows, macOS, 32-bit systems and headless playback are outside these setup paths.

[Hardware buying guide](buying.md) · [Pi-hole coexistence](../docs/pi-hole.md)

## Smaller boards: check before buying

These folders document experiments and limits, not verified hardware support:

| Board | Current verdict |
| --- | --- |
| [Pi Zero / Zero 2 W](raspberry-pi-zero-2-w/) | Original Zero is unsupported. Zero 2 W has a separate, unvalidated Lite experiment; 512MB may be insufficient. |
| [Pi 3 B / B+](raspberry-pi-3/) | Separate Raspberry Pi OS Lite experiment; no physical casting/playback validation yet. |
| [NanoPi](nanopi/) | A FriendlyELEC family, not a Raspberry Pi model. Evaluate each board's OS, TV output and drivers. |
| [ESP32 and Pico](esp32/) | Microcontrollers cannot run the current JetsonCast/Electron application. |

Only entries in `profiles.json` are selectable standard installer profiles.
The [Lite experiment](../experiments/pi-lite/) requires explicit `--lite` and
uses separate files/settings. Model-specific
x86 guides reuse `--device mini-pc`; they do not ship separate runtimes.

## Install and test

1. Start with the guide for your hardware. Turn on the TV, select its input, and open a terminal on your graphical desktop. The phone and computer should be on the same trusted LAN.
2. From the [cloned repository](../README.md#quick-start), run `python3 install.py`. Setup detects the CPU and recognized ARM boards. Use `python3 install.py devices` to list the guides, or `python3 install.py doctor` for a read-only host and installation check.
3. Open **Jetson Cast** from the app menu and finish the YouTube prompts. In the phone's YouTube app, open **Cast** and select your receiver. Play a video and verify that sound comes from the TV.

`python3 install.py --dry-run --non-interactive` previews the plan with no download or file changes, even without a graphical session. It cannot check the downloaded runtime libraries or predict playback. Optional login startup begins after you sign in. See [troubleshooting](../docs/compatibility.md#troubleshooting) for audio, discovery and fullscreen help.
