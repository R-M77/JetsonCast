import io
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest import mock


class SamsungXMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addons = Path(__file__).resolve().parents[1] / 'addons'
        script = str(addons / 'legacy_samsung.py')
        argv = [script, '--config', str(addons / 'config.example.json')]
        with (
            mock.patch.object(sys, 'argv', argv),
            mock.patch.dict(sys.modules, {'pychromecast': types.ModuleType('pychromecast')}),
            mock.patch('logging.basicConfig'),
            mock.patch('logging.getLogger'),
        ):
            cls.addon = runpy.run_path(script)

    def test_accepts_xml_at_size_limit(self):
        limit = self.addon['MAX_TV_XML_BYTES']
        response = io.BytesIO(b'<response/>'.ljust(limit))
        self.assertEqual(self.addon['read_tv_xml'](response).tag, 'response')

    def test_reads_only_one_extra_byte_before_rejecting_oversize_xml(self):
        limit = self.addon['MAX_TV_XML_BYTES']
        response = io.BytesIO(b'<response/>'.ljust(limit * 2))
        with self.assertRaisesRegex(ValueError, 'XML response exceeds size limit'):
            self.addon['read_tv_xml'](response)
        self.assertEqual(response.tell(), limit + 1)


if __name__ == '__main__':
    unittest.main()
