# JetsonCast Lite · Pi experiment

**Same YouTube-app casting and ad blocker. Fewer extras. Hardware testing needed.**

An opt-in route for **Pi 3 B/B+** and **Pi Zero 2 W** using Raspberry Pi OS
64-bit Bookworm or Trixie. It still runs Electron and YouTube's TV web app;
this is not a tiny native player. Pi 3 B/B+ is the first target to test.
Zero 2 W and Pi 3 A+ have only 512MB and may run out of memory or fail playback.
**Do not buy a board on the assumption this experiment works.**

| Kept | Reduced |
| --- | --- |
| YouTube mobile app → Cast → receiver | No GIF backgrounds, Jet animations or custom idle overlay |
| VacuumTube's application-level ad blocking | Upstream low-memory mode enabled |
| Fullscreen and per-app TV audio routing | H.264 filtering; VP8/VP9/AV1/WebM blocked by default |
| Upstream discovery and playback code | Touch/gamepad extras off; no optional TV input helper |

The standard Ubuntu edition is unchanged. Lite has its own application folder,
player profile, launcher and optional login entry, all named `jetson-cast-lite`.
Do not run both receivers concurrently: their discovery can compete.

## Try on a spare Pi

Use a **separate test card**, TV cable, suitable power supply and keyboard for
first setup. Keep existing DNS servers and other working devices as they are.
Original Pi Zero/Zero W and 32-bit OS images cannot use the ARM64 runtime.

1. Install **Raspberry Pi OS Lite 64-bit**, based on Debian 12 (Bookworm) or 13
   (Trixie), using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
   Configure your user and Wi-Fi in Imager. Sign in locally on the TV.
2. Add a small X11/Openbox session and audio stack using the
   [fresh-card setup](setup.md). A graphical session is still required; the
   word “Lite” does not mean headless video playback.
3. Get the project without downloading the large artwork. While the repository
   is private, your Git client must already have repository access:

   ```bash
   git clone --depth 1 --filter=blob:none --sparse https://github.com/R-M77/JetsonCast.git
   cd JetsonCast
   git sparse-checkout set src devices experiments/pi-lite docs
   python3 install.py --lite --dry-run --non-interactive
   python3 install.py --lite --non-interactive
   ```

4. From the Pi's **local text console**, start the receiver session:

   ```bash
   startx /bin/sh "$PWD/experiments/pi-lite/session.sh" -- -nolisten tcp
   ```

   If using an existing graphical desktop instead, run
   `~/.local/bin/jetson-cast-lite`. The manual session script is unnecessary there.
5. Complete YouTube's first-run prompts on the TV. On a phone on the same trusted
   LAN, open YouTube → Cast → **Jetson Cast Lite**. Start at **360p or 480p**;
   try 720p only after stable playback. These are test settings, not performance
   promises. Choose video quality in the TV player; Lite does not enforce a cap.

For a minimal session, configure the test card's display to 720p using its OS
display tools if available. Lite does not change display modes, swap, boot,
autologin, drivers, router settings, DNS or any other service.

## Controls and recovery

```bash
python3 install.py doctor --lite
python3 install.py configure --lite
python3 install.py uninstall --lite
```

Close the receiver before configuring or uninstalling it. Uninstall removes
only Lite's runtime and launchers; its private profile/settings remain for
reinstallation. Always include `--lite` when managing this edition.

The regular `--autostart` option creates a **desktop-login** entry; it does not
start X11 after boot on a console-only card. Keep initial testing manual.

In VacuumTube settings (`Ctrl+O`), **Low Memory Mode**, **Filter Video Codecs**,
**Ad Blocker** and **Device Discoverability** are enabled on first install.
Subsequent installs preserve your settings. If a video has no playable format,
try disabling codec filtering there; this can increase decoding cost.
H.264 selection does **not** prove hardware decoding: Electron's graphics path
may not use the board's decoder. Do not disable the GPU or sandbox to force it.

## What has been verified

- Installer tests cover edition isolation, target selection, a fresh staged
  install, repeat install, dry run and uninstall using synthetic runtime files.
- The pinned ARM64 archive's SHA-256 and Lite patch were checked. Upstream
  DIAL, ad-blocking, codec-filter and low-memory modules remain unchanged.
- Standard-edition patched archive output was byte-identical to the previous
  implementation on the same pinned release.
- Lite omits **66.44 MiB of installed artwork**. That is a disk-size measurement,
  not measured RAM savings. The Electron download itself is the same size.
- **No physical Pi launch, casting, TV audio, memory or sustained playback test
  has been completed.** This is an implementation ready for testing, not a
  supported appliance image.

Before calling a board supported, test fresh installation, phone discovery,
play/pause/seek, TV audio, three reconnects and at least 30 minutes of varied
playback. Check for out-of-memory exits, persistent swapping, dropped frames
and thermal throttling. Record OS, board/RAM, resolution and codec alongside
results. `free -m`, `vmstat 1` and YouTube's Stats for Nerds can help locally;
do not publish raw profiles, account details, video history or screenshots.
An ad-free play alone does not establish ad-blocking effectiveness.

If Zero 2 W remains unstable, stop there. A browser-free player would need a
separate implementation of YouTube's phone-control protocol and stream handling;
simply using an MPV URL player would not preserve this casting workflow.
Use a more capable host for Pi-hole alongside playback until shared load is tested.

## Sources

[VacuumTube 2.0.1 configuration](https://github.com/shy1132/VacuumTube/blob/v2.0.1/src/config.js)
· [Low-memory implementation](https://github.com/shy1132/VacuumTube/blob/v2.0.1/src/preload/modules/low-memory-mode.js)
· [DIAL implementation](https://github.com/shy1132/VacuumTube/tree/v2.0.1/src/preload/modules/h5vcc)
· [Raspberry Pi OS](https://www.raspberrypi.com/documentation/computers/os.html)
· [Security limits](../../SECURITY.md)

[Back to hardware choices](../../devices/buying.md)
