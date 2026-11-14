#!/usr/bin/env python3
"""Launch the receiver and its bounded app-only audio watcher."""
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
from audio import watch


def main():
    base = Path(__file__).resolve().parent.parent
    config = json.loads((base / 'settings.json').read_text())
    runtime = (base / 'runtime').resolve()
    env = os.environ.copy()
    env['JETSON_CAST_HOME'] = str(base)
    env['JETSON_CAST_NAME'] = config['name']
    env['JETSON_CAST_ROTATION'] = str(config['rotation_seconds'])
    env['JETSON_CAST_FUN_MODE'] = '1' if config.get('fun_mode') is True and config.get('edition') != 'lite' else '0'
    env['JETSON_CAST_INPUT_SWITCH'] = '1' if config.get('input_switch') and config.get('edition') != 'lite' else '0'
    env.pop('PULSE_SINK', None)
    # Upstream Steam game mode adds --no-sandbox; this desktop package must not.
    env.pop('SteamOS', None)
    env.pop('SteamGamepadUI', None)
    # No --no-sandbox, debug ports, or unauthenticated remote administration.
    child = subprocess.Popen([str(runtime / 'vacuumtube'), '--portable=' + str(base / 'profile'), '--fullscreen'], env=env)
    stop = threading.Event()
    watcher = threading.Thread(target=watch, args=(stop, runtime, config.get('audio_sink')), daemon=True)
    watcher.start()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: child.terminate() if child.poll() is None else None)
    try:
        return child.wait()
    finally:
        stop.set()
        watcher.join(timeout=6)


if __name__ == '__main__':
    raise SystemExit(main())
