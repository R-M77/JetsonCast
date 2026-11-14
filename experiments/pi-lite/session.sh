#!/bin/sh
# Optional, manually started X11 session on a dedicated Pi OS Lite test card.
set -eu
if [ -z "${DISPLAY:-}" ]; then
    echo 'Start this script with startx; see experiments/pi-lite/README.md.' >&2
    exit 1
fi
if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
    exec dbus-run-session -- /bin/sh "$0"
fi
if [ ! -x "$HOME/.local/bin/jetson-cast-lite" ]; then
    echo 'Install with python3 install.py --lite --non-interactive first.' >&2
    exit 1
fi
# Reuse an existing PulseAudio/PipeWire server; never stop or replace it.
if ! pactl info >/dev/null 2>&1; then
    pulseaudio --start --exit-idle-time=-1
fi
openbox --sm-disable &
wm_pid=$!
trap 'kill "$wm_pid" 2>/dev/null || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
"$HOME/.local/bin/jetson-cast-lite"
