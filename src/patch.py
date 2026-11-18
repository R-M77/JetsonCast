"""Version-checked customization; never patch an unknown upstream layout."""
import json
from pathlib import Path
from asar import read, pack


def customize(archive, module_dir, lite=False):
    files = read(archive)
    if json.loads(files['package.json'][0])['version'] != '2.1.1':
        raise ValueError('Unsupported VacuumTube version; refusing to patch')

    def replace(name, old, new):
        data, executable = files[name]
        text = data.decode()
        if text.count(old) != 1:
            raise ValueError('Upstream layout mismatch: ' + name)
        files[name] = (text.replace(old, new).encode(), executable)

    replace('src/preload/modules/h5vcc/dial/server.js',
            "el('friendlyName', `${constants.hostname} (VacuumTube)`)",
            "el('friendlyName', process.env.JETSON_CAST_NAME || 'Jetson Cast')")
    replace('src/preload/modules/cast-label.js',
            'mdx_device_label: `${hostname} (VacuumTube)`',
            "mdx_device_label: process.env.JETSON_CAST_NAME || 'Jetson Cast'")
    replace('src/index.js', 'await electron.app.whenReady()',
            "await electron.app.whenReady()\n    electron.powerSaveBlocker.start('prevent-display-sleep')")
    replace('src/index.js', '    // Ensure the *content* area', '''    // Keep the TV fullscreen after a display reconnect, without changing desktop settings.
    const fitTV = () => {
        if (win.isDestroyed() || !(argv.fullscreen || configManager.get().fullscreen)) return;
        win.setBounds(electron.screen.getDisplayMatching(win.getBounds()).bounds);
        win.setFullScreen(true);
    };
    electron.screen.on('display-added', fitTV);
    electron.screen.on('display-metrics-changed', fitTV);
    win.once('closed', () => {
        electron.screen.removeListener('display-added', fitTV);
        electron.screen.removeListener('display-metrics-changed', fitTV);
    });

    // Ensure the *content* area''')
    # Lite retains upstream DIAL, ad blocking and low-memory handling unchanged.
    # Omit the optional modules entirely: no timers, GIF decoding or input helper.
    for name in (() if lite else ('ambient.js', 'input-intent.js')):
        files['src/preload/modules/jetson-' + name] = ((Path(module_dir) / name).read_bytes(), False)
    return pack(files)
