import argparse
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('device_installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
UBUNTU = {'ID': 'ubuntu', 'VERSION_ID': '22.04'}


class DeviceSelectionTests(unittest.TestCase):
    def select(self, requested='auto', machine='x86_64', bits=64, os_release=None, model=''):
        return installer.select_device(requested, machine, bits, UBUNTU if os_release is None else os_release, model)

    def test_cpu_aliases_and_generic_fallback(self):
        for machine, expected in (('AMD64', ('x86-pc', 'x86_64')), ('arm64', ('generic-arm64', 'aarch64'))):
            self.assertEqual(self.select(machine=machine)[:2], expected)

    def test_rejects_unsupported_cpu_and_32_bit_userspace(self):
        for machine, bits in (('armv7l', 32), ('i686', 32), ('riscv64', 64), ('aarch64', 32), ('x86_64', 32)):
            with self.subTest(machine=machine, bits=bits), self.assertRaisesRegex(ValueError, '64-bit Ubuntu'):
                self.select(machine=machine, bits=bits)

    def test_rejects_other_operating_systems_and_releases(self):
        for release in ({}, {'ID': 'debian', 'VERSION_ID': '12'}, {'ID': 'ubuntu', 'VERSION_ID': '20.04'},
                        {'ID': 'ubuntu', 'VERSION_ID': '26.04'}, {'ID': 'linuxmint', 'ID_LIKE': 'ubuntu', 'VERSION_ID': '22.04'}):
            with self.subTest(release=release), self.assertRaisesRegex(ValueError, 'Ubuntu 22.04 or 24.04'):
                self.select(os_release=release)

    def test_board_auto_detection_and_pi_400_does_not_match_pi_4(self):
        for model, expected in (('NVIDIA Jetson Orin Nano Developer Kit', 'jetson-orin-nano'),
                                ('Raspberry Pi 4 Model B Rev 1.5', 'raspberry-pi-4'),
                                ('Raspberry Pi 400 Rev 1.0', 'generic-arm64')):
            self.assertEqual(self.select(machine='aarch64', model=model)[0], expected)

    def test_pi_5_requires_24_04_even_with_generic_override(self):
        model = 'Raspberry Pi 5 Model B Rev 1.0'
        for requested in ('auto', 'raspberry-pi-5', 'generic-arm64'):
            with self.subTest(requested=requested), self.assertRaisesRegex(ValueError, 'needs Ubuntu 24.04'):
                self.select(requested, machine='aarch64', model=model)
        self.assertEqual(self.select(machine='aarch64', model=model,
                                     os_release={'ID': 'ubuntu', 'VERSION_ID': '24.04'})[0], 'raspberry-pi-5')

    def test_rejects_wrong_architecture_and_wrong_detected_board(self):
        with self.assertRaisesRegex(ValueError, 'requires aarch64'):
            self.select('jetson-orin-nano')
        with self.assertRaisesRegex(ValueError, 'requires x86_64'):
            self.select('mini-pc', machine='aarch64')
        with self.assertRaisesRegex(ValueError, 'not Raspberry Pi 4'):
            self.select('raspberry-pi-4', machine='aarch64', model='NVIDIA Jetson Orin Nano Developer Kit')

    def test_profiles_have_guides_and_share_existing_archives(self):
        for key, profile in installer.DEVICE_PROFILES.items():
            with self.subTest(key=key):
                self.assertTrue((ROOT / 'devices' / key / 'README.md').is_file())
                self.assertIn(profile['architecture'], installer.RELEASES)


class PreflightTests(unittest.TestCase):
    def test_display_session(self):
        self.assertIsNone(installer.desktop_session({}))
        self.assertEqual(installer.desktop_session({'DISPLAY': ':0'}), 'X11')
        self.assertEqual(installer.desktop_session({'DISPLAY': ':0', 'WAYLAND_DISPLAY': 'wayland-0'}), 'Wayland')

    def test_cli_dry_run_accepts_headless_host_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            locations = (root / 'app', root / 'bin/jetson-cast', root / 'apps/cast.desktop', root / 'start/cast.desktop')
            output = io.StringIO()
            with patch.object(sys, 'argv', ['install.py', '--dry-run', '--non-interactive']), \
                 patch.object(sys, 'platform', 'linux'), \
                 patch.object(os, 'geteuid', return_value=1000, create=True), \
                 patch.object(installer.platform, 'freedesktop_os_release', return_value=UBUNTU, create=True), \
                 patch.object(installer.platform, 'machine', return_value='x86_64'), \
                 patch.object(installer.struct, 'calcsize', return_value=8), \
                 patch.object(installer, 'locations', return_value=locations), \
                 patch.object(installer.shutil, 'which', return_value=None), \
                 patch.dict(os.environ, {}, clear=True), \
                 patch.object(installer, 'download') as download, \
                 contextlib.redirect_stdout(output):
                self.assertEqual(installer.main(), 0)
            self.assertIn('no display detected', output.getvalue())
            self.assertIn('Plan: VacuumTube', output.getvalue())
            download.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])

    def test_missing_library_prevents_install_commit(self):
        def extracted(_archive, destination):
            runtime = destination / 'runtime'
            (runtime / 'resources').mkdir(parents=True)
            (runtime / 'resources/app.asar').write_bytes(b'not patched')
            (runtime / 'vacuumtube').write_bytes(b'fake ELF; never executed')

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            locations = (root / 'data/app', root / 'bin/cast', root / 'apps/cast.desktop', root / 'start/cast.desktop')
            args = argparse.Namespace(device='auto', dry_run=False, non_interactive=True, autostart=False)
            with patch.object(installer, 'preflight', return_value=('x86_64', 'X11', 'ldd')), \
                 patch.object(installer, 'locations', return_value=locations), \
                 patch.object(installer, 'download'), \
                 patch.object(installer, 'extract_checked', side_effect=extracted), \
                 patch.object(installer.subprocess, 'run', return_value=subprocess.CompletedProcess(
                     ['ldd'], 0, '\tlibgtk-3.so.0 => not found\n', '')), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'Missing desktop libraries: libgtk-3.so.0'):
                    installer.install(args)
            self.assertTrue(all(not path.exists() for path in locations))
            self.assertEqual(list((root / 'data').iterdir()), [])

    def test_runtime_dependency_check_reports_abi_failure(self):
        result = subprocess.CompletedProcess(['ldd'], 1, '', 'runtime cannot load this ABI')
        with patch.object(installer.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'Could not check the runtime libraries'):
                installer.missing_runtime_libraries('ldd', Path('runtime/vacuumtube'))

    def test_dry_run_cannot_silently_uninstall(self):
        with patch.object(sys, 'argv', ['install.py', 'uninstall', '--dry-run', '--yes']), \
             patch.object(installer, 'uninstall') as uninstall, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                installer.main()
            self.assertEqual(error.exception.code, 2)
            uninstall.assert_not_called()


if __name__ == '__main__':
    unittest.main()
