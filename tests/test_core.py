import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
import asar
import privacy_check
spec = importlib.util.spec_from_file_location('installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ArchiveTests(unittest.TestCase):
    def test_asar_roundtrip_and_integrity(self):
        files = {'src/a.js': (b'hello', False), 'run': (b'#!/bin/sh\n', True)}
        blob = asar.pack(files)
        self.assertEqual(asar.read(blob), files)
        header = json.loads(blob[16:16+struct.unpack('<I', blob[12:16])[0]])
        self.assertEqual(header['files']['src']['files']['a.js']['integrity']['algorithm'], 'SHA256')

    def test_asar_rejects_truncation_and_traversal(self):
        with self.assertRaises(ValueError): asar.read(b'broken')
        with self.assertRaises(ValueError): asar.pack({'../outside': (b'x', False)})
        blob = asar.pack({'a': (b'hello', False)})
        with self.assertRaises(ValueError): asar.read(blob[:-2])

    def test_tar_rejects_path_traversal_and_links(self):
        for name, kind in (('../escape', tarfile.REGTYPE), ('safe-link', tarfile.SYMTYPE), ('/absolute', tarfile.REGTYPE)):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp); archive = root / 'a.tar.gz'; dest = root / 'dest'; dest.mkdir()
                with tarfile.open(archive, 'w:gz') as tar:
                    member = tarfile.TarInfo(name); member.type = kind; member.linkname = '../../escape'; member.size = 0
                    tar.addfile(member, io.BytesIO())
                with self.assertRaises(ValueError): installer.extract_checked(archive, dest)
                self.assertEqual(list(dest.iterdir()), [])

    def test_tar_clears_special_permissions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); dest = root / 'out'; dest.mkdir(); archive = root / 'a.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                member = tarfile.TarInfo('bin/app'); member.mode = 0o6777; member.size = 2
                tar.addfile(member, io.BytesIO(b'ok'))
            installer.extract_checked(archive, dest)
            self.assertEqual((dest / 'bin/app').read_bytes(), b'ok')
            if sys.platform != 'win32': self.assertEqual((dest / 'bin/app').stat().st_mode & 0o7777, 0o755)


class SafetyTests(unittest.TestCase):
    def test_atomic_write_does_not_overwrite_hardlink_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); original = root / 'unrelated'; managed = root / 'managed'
            original.write_text('keep this')
            try: managed.hardlink_to(original)
            except OSError: self.skipTest('Hardlinks not supported')
            installer.write_private(managed, 'new app data')
            self.assertEqual(original.read_text(), 'keep this')
            self.assertEqual(managed.read_text(), 'new app data')

    def test_atomic_write_rejects_parent_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); outside = root / 'outside'; outside.mkdir(); link = root / 'link'
            try: link.symlink_to(outside, target_is_directory=True)
            except OSError: self.skipTest('Symlinks not permitted')
            with self.assertRaises(ValueError): installer.write_private(link / 'file', 'data')
            self.assertEqual(list(outside.iterdir()), [])

    def test_marker_requires_exact_line(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'entry'
            file.write_text('unrelated ' + installer.MARKER + ' contents')
            self.assertFalse(installer.owned(file))
            file.write_text('# ' + installer.MARKER + '\n')
            self.assertTrue(installer.owned(file))

    def test_settings_are_plain_data(self):
        self.assertEqual(installer.validate_settings({'name': 'Kitchen TV', 'rotation_seconds': 300})['name'], 'Kitchen TV')
        for config in ({'name': 'bad\nname'}, {'name': 'ok', 'rotation_seconds': -1}, {'name': 'ok', 'audio_sink': 'bad\noutput'}):
            with self.assertRaises(ValueError): installer.validate_settings(config)

    def test_fun_mode_is_opt_in_and_configurable(self):
        self.assertFalse(installer.choose_settings(interactive=False)['fun_mode'])
        self.assertFalse(installer.choose_settings({'name': 'TV'}, interactive=False)['fun_mode'])
        for answer, expected in [('yes', True), ('no', False)]:
            with patch('builtins.input', side_effect=['', '', answer, '']), patch('audio.query', return_value=[]):
                config = installer.choose_settings({'name': 'TV', 'fun_mode': not expected})
            self.assertIs(config['fun_mode'], expected)
        with patch('builtins.input', side_effect=['', '', '', '']), patch('audio.query', return_value=[]):
            self.assertTrue(installer.choose_settings({'name': 'TV', 'fun_mode': True})['fun_mode'])
        self.assertFalse(installer.choose_settings({'name': 'TV', 'edition': 'lite', 'fun_mode': True}, False)['fun_mode'])
        for invalid in ('false', 1, None):
            with self.assertRaises(ValueError):
                installer.validate_settings({'name': 'TV', 'fun_mode': invalid})

    def test_launcher_passes_explicit_fun_mode_without_inheriting_it(self):
        import launch
        for config, expected in [({}, '0'), ({'fun_mode': True}, '1'),
                                 ({'fun_mode': False}, '0'),
                                 ({'fun_mode': True, 'edition': 'lite'}, '0')]:
            settings = {'name': 'TV', 'rotation_seconds': 300, **config}
            with patch.object(launch.Path, 'read_text', return_value=json.dumps(settings)), \
                 patch.dict(launch.os.environ, {'JETSON_CAST_FUN_MODE': '1'}), \
                 patch.object(launch.subprocess, 'Popen') as popen, \
                 patch.object(launch.threading, 'Thread'), patch.object(launch.signal, 'signal'):
                launch.main()
            self.assertEqual(popen.call_args.kwargs['env']['JETSON_CAST_FUN_MODE'], expected)

    def test_privacy_guard(self):
        # Build fixtures without embedding a plausible secret or private address in Git.
        self.assertIn('access-token', privacy_check.text_findings('gh' + 'p_' + 'a' * 36))
        self.assertIn('private-LAN-address', privacy_check.text_findings('.'.join(['10', '7', '8', '9'])))
        self.assertIn('personal-home-path', privacy_check.text_findings('/' + 'home/' + 'example' + '/app'))
        self.assertEqual(privacy_check.text_findings('https://github.com/R-M77/JetsonCast'), [])

    def test_assets_have_no_embedded_metadata(self):
        for file in (ROOT / 'assets').rglob('*'):
            if file.is_file():
                with self.subTest(file=str(file.relative_to(ROOT))):
                    self.assertEqual(privacy_check.inspect(file.relative_to(ROOT).as_posix(), file.read_bytes()), [])

    def test_audio_only_moves_receiver_stream(self):
        import audio
        streams = [{'index': 1, 'sink': 4}, {'index': 2, 'sink': 4}, {'index': 3, 'sink': 5}]
        with patch.object(audio, 'query', side_effect=lambda kind: [{'name': 'tv-output', 'index': 5}] if kind == 'sinks' else streams), patch.object(audio, 'owned_stream', side_effect=lambda s, _: s['index'] != 2), patch.object(audio.subprocess, 'run') as run:
            audio.route(Path('/test-runtime'), 'tv-output')
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0], ['pactl', 'move-sink-input', '1', 'tv-output'])


if __name__ == '__main__': unittest.main()
