"""Route only this isolated receiver's streams; never change the default sink."""
import json
import os
import subprocess
import time


def query(kind):
    return json.loads(subprocess.check_output(
        ['pactl', '--format=json', 'list', kind], timeout=5, stderr=subprocess.DEVNULL))


def owned_stream(stream, runtime):
    props = stream.get('properties', {})
    try:
        pid = int(props['application.process.id'])
        executable = os.path.realpath('/proc/' + str(pid) + '/exe')
        return executable == str(runtime / 'vacuumtube')
    except (KeyError, ValueError, OSError):
        return False


def route(runtime, sink_name):
    if not sink_name:
        return
    target = next((s for s in query('sinks') if s['name'] == sink_name), None)
    if target is None:
        return
    for stream in query('sink-inputs'):
        if owned_stream(stream, runtime) and stream['sink'] != target['index']:
            subprocess.run(['pactl', 'move-sink-input', str(stream['index']), sink_name],
                           check=True, timeout=5, stderr=subprocess.DEVNULL)


def watch(stop, runtime, sink_name):
    while not stop.is_set():
        try:
            route(runtime, sink_name)
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
        stop.wait(3)
