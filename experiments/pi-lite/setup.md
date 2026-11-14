# Minimal graphical session on a fresh test card

These optional commands are for **a spare Raspberry Pi OS Lite 64-bit card**.
They install OS packages and need administrator privileges. JetsonCast's
installer itself runs without sudo. Do not apply this recipe to a working
Jetson, DNS server or an existing desktop/audio configuration.

First confirm the OS release in `/etc/os-release`. Use the matching block:

**Bookworm / Debian 12:**

```bash
sudo apt update
sudo apt install --no-install-recommends python3 git ca-certificates \
  xserver-xorg xinit openbox dbus-x11 pulseaudio pulseaudio-utils \
  libgtk-3-0 libasound2 libnss3 libgbm1 libxss1 libxtst6 \
  libdrm2 libxkbcommon0 libgl1-mesa-dri fonts-dejavu-core
```

**Trixie / Debian 13:**

```bash
sudo apt update
sudo apt install --no-install-recommends python3 git ca-certificates \
  xserver-xorg xinit openbox dbus-x11 pulseaudio pulseaudio-utils \
  libgtk-3-0t64 libasound2t64 libnss3 libgbm1 libxss1 libxtst6 \
  libdrm2 libxkbcommon0 libgl1-mesa-dri fonts-dejavu-core
```

This deliberately omits a desktop shell, web browser, office suite and display
manager. Package names and dependencies can change. The installer runs `ldd`
against the verified runtime and stops before installing it if libraries are
missing. Look up any missing library in your release's package index; do not
mix Ubuntu packages into Raspberry Pi OS.

Return to the [Lite quick start](README.md#try-on-a-spare-pi) to install and
start X11 locally. `session.sh` starts a session D-Bus when needed, reuses a
working PulseAudio/PipeWire server or starts user PulseAudio, launches Openbox
without its desktop autostart programs, then runs the Lite receiver. It closes
only its own Openbox process when the receiver exits. It neither enables boot
services nor changes login security.

For audio, first confirm HDMI sound works in the OS. With the graphical session
running, `python3 install.py configure --lite` can select an available TV sink
from another terminal. It routes only receiver streams, leaving the system
default alone. Restart the receiver to apply settings.

An existing Raspberry Pi OS desktop is also an experimental option, but consumes
more memory. Keep its audio stack and run the Lite launcher directly. If startup
fails due to a sandbox policy, consult your OS documentation rather than adding
`--no-sandbox`. No automatic sandbox or driver workarounds are included.

This recipe has been reviewed but not exercised on physical Pi hardware.
[Raspberry Pi OS documentation](https://www.raspberrypi.com/documentation/computers/os.html)
· [Debian xinit](https://packages.debian.org/bookworm/xinit)
· [Bookworm audio library](https://packages.debian.org/bookworm/libasound2)
· [Trixie audio library](https://packages.debian.org/trixie/libasound2t64)
