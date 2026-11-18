"""Lite regression checks; these do not substitute for a physical Pi test."""
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import asar
import audio
import lite
import patch as customization

spec = importlib.util.spec_from_file_location('lite_installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def upstream_fixture():
    # Small synthetic layout; the pinned release is checked separately before shipping.
    return asar.pack({
        'package.json': (b'{"version":"2.1.1"}', False),
        'src/index.js': (b'await electron.app.whenReady()\n    // Ensure the *content* area', False),
        'src/preload/modules/h5vcc/dial/server.js':
            (b"el('friendlyName', `${constants.hostname} (VacuumTube)`)", False),
        'src/preload/modules/cast-label.js': (b'mdx_device_label: `${hostname} (VacuumTube)`', False),
        'src/preload/modules/h5vcc/dial/http.js': (b'keep DIAL transport', False),
        'src/preload/modules/adblock.js': (b'keep ad blocker', False),
        'src/preload/modules/low-memory-mode.js': (b'keep low-memory handler', False),
    })


class LiteTests(unittest.TestCase):
    def test_target_matrix_is_opt_in_and_bounded(self):
        for model in ('Raspberry Pi Zero 2 W Rev 1.0', 'Raspberry Pi 3 Model B Rev 1.2',
                      'Raspberry Pi 3 Model B Plus Rev 1.3', 'Raspberry Pi 3 Model A Plus Rev 1.0'):
            for version in ('12', '13'):
                release = {'ID': 'debian', 'VERSION_ID': version}
                self.assertTrue(lite.select_lite('aarch64', 64, release, model))
                with self.assertRaises(ValueError):
                    installer.select_device('auto', 'aarch64', 64, release, model)
        for machine, bits, release, model in (
            ('armv7l', 32, {'ID': 'debian', 'VERSION_ID': '12'}, 'Raspberry Pi 3 Model B Rev 1.2'),
            ('aarch64', 64, {'ID': 'ubuntu', 'VERSION_ID': '22.04'}, 'Raspberry Pi 3 Model B Rev 1.2'),
            ('aarch64', 64, {'ID': 'debian', 'VERSION_ID': '11'}, 'Raspberry Pi Zero 2 W Rev 1.0'),
            ('aarch64', 64, {'ID': 'debian', 'VERSION_ID': '13'}, 'NVIDIA Jetson Orin Nano'),
            ('aarch64', 64, {'ID': 'debian', 'VERSION_ID': '13'}, 'Raspberry Pi Zero W Rev 1.1'),
        ):
            with self.subTest(model=model, release=release), self.assertRaises(ValueError):
                lite.select_lite(machine, bits, release, model)

    def test_defaults_preserve_casting_adblock_and_standard_behavior(self):
        self.assertEqual(lite.player_defaults(), {'adblock': True, 'fullscreen': True,
                          'device_discoverability': True, 'auto_update': False})
        config = lite.player_defaults(True)
        for key in ('adblock', 'device_discoverability', 'low_memory_mode', 'h264ify', 'hardware_decoding'):
            self.assertIs(config[key], True)
        self.assertFalse(config['unlock_resolution'])
        self.assertEqual(lite.asset_names(True), ())
        self.assertEqual(len(lite.asset_names()), 7)

    def test_lite_patch_omits_optional_modules_preserves_core(self):
        original = upstream_fixture()
        # Deliberately no asset/module files: sparse Lite checkouts must work.
        with tempfile.TemporaryDirectory() as temp:
            result = asar.read(customization.customize(original, Path(temp), lite=True))
        for name, content in asar.read(original).items():
            if name not in ('src/index.js', 'src/preload/modules/h5vcc/dial/server.js',
                            'src/preload/modules/cast-label.js'):
                self.assertEqual(result[name], content)
        self.assertFalse(any('jetson-' in name for name in result))
        standard = asar.read(customization.customize(original, ROOT / 'src'))
        for name in ('ambient.js', 'input-intent.js'):
            self.assertIn('src/preload/modules/jetson-' + name, standard)

    def test_locations_and_desktop_entries_are_separate(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(installer.Path, 'home', return_value=Path(temp)), \
             patch.dict(os.environ, {'XDG_DATA_HOME': temp + '/data', 'XDG_CONFIG_HOME': temp + '/config'}):
            standard, light = installer.locations(), installer.locations(True)
        self.assertFalse(set(standard) & set(light))
        self.assertIn('Name=Jetson Cast\n', installer.desktop_text(standard[0]))
        self.assertIn('Name=Jetson Cast Lite\n', installer.desktop_text(light[0], True))

    def test_lite_install_and_uninstall_leave_standard_files_intact(self):
        def extracted(_archive, destination):
            runtime = destination / 'runtime'
            (runtime / 'resources').mkdir(parents=True)
            (runtime / 'resources/app.asar').write_bytes(upstream_fixture())
            (runtime / 'vacuumtube').write_bytes(b'fake ELF; never executed')

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(installer.Path, 'home', return_value=root), \
                 patch.dict(os.environ, {'XDG_DATA_HOME': str(root / 'data'), 'XDG_CONFIG_HOME': str(root / 'config')}):
                standard = installer.locations()
                for path in standard:
                    if path == standard[0]:
                        path.mkdir(parents=True)
                        (path / 'keep').write_bytes(b'unchanged standard application')
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(b'unchanged standard launcher')
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                args = argparse.Namespace(lite=True, dry_run=False, non_interactive=True, autostart=True, yes=True)
                with patch.object(installer, 'preflight', return_value=('aarch64', 'X11', 'ldd')), \
                     patch.object(installer, 'download'), \
                     patch.object(installer, 'extract_checked', side_effect=extracted), \
                     patch.object(installer, 'missing_runtime_libraries', return_value=[]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    installer.install(args)
                base, launcher, desktop, autostart = installer.locations(True)
                self.assertTrue(all(p.exists() for p in (base, launcher, desktop, autostart)))
                self.assertFalse((base / 'ambient').exists())
                self.assertFalse((base / 'src/ambient.js').exists())
                self.assertFalse((base / 'src/input-intent.js').exists())
                config = json.loads((base / 'profile/config.json').read_text())
                self.assertEqual(config, lite.player_defaults(True))
                settings = json.loads((base / 'settings.json').read_text())
                self.assertEqual(settings['edition'], 'lite')
                # Rerun must preserve a user's settings, not reset the player profile.
                config['volume'] = 27
                (base / 'profile/config.json').write_text(json.dumps(config))
                with patch.object(installer, 'preflight', return_value=('aarch64', 'X11', 'ldd')), \
                     patch.object(installer, 'download') as download, contextlib.redirect_stdout(io.StringIO()):
                    installer.install(args)
                    download.assert_not_called()
                self.assertEqual(json.loads((base / 'profile/config.json').read_text())['volume'], 27)
                with contextlib.redirect_stdout(io.StringIO()):
                    installer.uninstall(args)
                self.assertFalse((base / 'runtime').exists())
                self.assertTrue((base / 'profile/config.json').exists())
                self.assertTrue((base / 'settings.json').exists())
                self.assertTrue(all(not p.exists() for p in (launcher, desktop, autostart)))
                self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_lite_dry_run_writes_and_downloads_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = (root / 'app', root / 'launcher', root / 'desktop', root / 'autostart')
            args = argparse.Namespace(lite=True, dry_run=True, non_interactive=True, autostart=False)
            with patch.object(installer, 'preflight', return_value=('aarch64', None, None)), \
                 patch.object(installer, 'locations', return_value=paths), \
                 patch.object(installer, 'download') as download, contextlib.redirect_stdout(io.StringIO()):
                installer.install(args)
            download.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])

    def test_lite_configure_uses_only_lite_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = (root / 'app', root / 'launcher', root / 'desktop', root / 'autostart')
            base = paths[0]
            base.mkdir()
            (base / 'INSTALLATION').write_text(installer.MARKER + '\n')
            initial = {'name': 'Jetson Cast Lite', 'edition': 'lite', 'rotation_seconds': 300, 'audio_sink': ''}
            (base / 'settings.json').write_text(json.dumps(initial))
            with patch.object(installer, 'locations', return_value=paths) as locations, \
                 patch.object(audio, 'query', return_value=[]), \
                 patch('builtins.input', side_effect=['Test receiver', '', 'n']), \
                 contextlib.redirect_stdout(io.StringIO()):
                installer.configure(argparse.Namespace(lite=True))
            locations.assert_called_once_with(True)
            saved = json.loads((base / 'settings.json').read_text())
            self.assertEqual(saved['name'], 'Test receiver')
            self.assertEqual(saved['edition'], 'lite')
            self.assertFalse(paths[3].exists())

    def test_lite_cli_preflight_detects_board_and_rejects_other_hosts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = (root / 'app', root / 'launcher', root / 'desktop', root / 'autostart')
            with patch.object(sys, 'argv', ['install.py', '--lite', '--dry-run', '--non-interactive']), \
                 patch.object(sys, 'platform', 'linux'), \
                 patch.object(os, 'geteuid', return_value=1000, create=True), \
                 patch.object(installer.platform, 'freedesktop_os_release',
                              return_value={'ID': 'debian', 'VERSION_ID': '13'}, create=True), \
                 patch.object(installer.platform, 'machine', return_value='aarch64'), \
                 patch.object(installer.struct, 'calcsize', return_value=8), \
                 patch.object(installer.Path, 'read_text', return_value='Raspberry Pi Zero 2 W Rev 1.0\0') as read, \
                 patch.object(installer, 'locations', return_value=paths), \
                 patch.object(installer.shutil, 'which', return_value=None), \
                 patch.dict(os.environ, {}, clear=True), \
                 patch.object(installer, 'download') as download, \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(installer.main(), 0)
                read.return_value = 'NVIDIA Jetson Orin Nano Developer Kit'
                self.assertEqual(installer.main(), 1)
                download.assert_not_called()
                self.assertEqual(list(root.iterdir()), [])

    def test_lite_cannot_be_mixed_with_standard_device_override(self):
        with patch.object(sys, 'argv', ['install.py', '--lite', '--device', 'jetson-orin-nano']), \
             contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            installer.main()
        self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
