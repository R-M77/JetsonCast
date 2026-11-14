# Optional: two receivers, one TV

**Experimental, advanced setup. Off by default.** This is a separately run
helper for older Samsung TVs exposing the `MainTVAgent2:1` UPnP service.
It is not a universal HDMI or HDMI-CEC controller. TV remote play/pause is
not forwarded to Jetson Cast.

YouTube playback can select the Linux input. Prime/Plex playback on an
existing Chromecast can select the Chromecast input and pause the other
player. The original phone apps still target two different receivers.

1. Confirm both inputs work with the TV remote, including return to Linux
   with picture **and sound**. DP-to-HDMI adapters can lose their display
   handshake during switching. If this happens, disable this helper; a TV
   power cycle may recover it. Do not reset a shared Linux host to compensate.
2. Obtain your TV's local UPnP control URL, UDN and source IDs from its device
   description / `GetSourceList`. Obtain your Chromecast UUID from local Cast
   discovery. Models vary; do not copy another person's source IDs blindly.
3. Copy `config.example.json` to your **installed user data directory** at
   `~/.local/share/jetson-cast/state/config.json`, create the directory with
   mode 700 and set the file to mode 600. Fill in your own device values.
   Respect `XDG_DATA_HOME` if customized. Never commit that private file.
4. In the installed `settings.json`, set `"input_switch": true`, and reopen
   Jetson Cast. This enables only local playback-intent files.
5. Install the optional controller separately and run it in a terminal:

```sh
python3 -m venv ~/.local/share/jetson-cast/controller-env
~/.local/share/jetson-cast/controller-env/bin/pip install 'PyChromecast==13.1.0'
~/.local/share/jetson-cast/controller-env/bin/python addons/legacy_samsung.py
```

Ubuntu may need the `python3-venv` package. The core installer does not install
or launch this helper. Stop with Ctrl+C; set `input_switch` back to false to
disable local events. Verify switching manually before arranging startup.
PyChromecast and its dependencies are external code, installed only by this
explicit optional step. App IDs and Cast receiver behavior can change.

Only trust your own LAN devices. UPnP control is not encrypted or
authenticated. No port forwarding, router DNS changes or firewall changes
are required by this helper. It never powers the TV on/off.
