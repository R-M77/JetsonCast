import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import privacy_check


class PrivacyVideoTests(unittest.TestCase):
    def test_accepts_only_reviewed_versions_at_the_exact_preview_path(self):
        path = 'assets/previews/sample.mp4'
        current = b'\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2'
        previous = current + b'older reviewed edit'
        fingerprints = {hashlib.sha256(data).hexdigest() for data in (current, previous)}
        approvals = {path: fingerprints, 'assets/sample.mp4': fingerprints}

        with mock.patch.dict(privacy_check.REVIEWED_PREVIEW_MP4S, approvals, clear=True):
            self.assertEqual(privacy_check.inspect(path, current), [])
            self.assertEqual(privacy_check.inspect(path, previous), [])
            self.assertEqual(privacy_check.inspect(path, current + b'changed'), ['unreviewed-MP4'])
            self.assertEqual(privacy_check.inspect('assets/previews/other.mp4', current), ['unreviewed-MP4'])
            self.assertEqual(privacy_check.inspect('assets/previews/sample.txt', current), ['unreviewed-MP4'])
            self.assertEqual(privacy_check.inspect('assets/sample.mp4', current), ['unreviewed-MP4'])


if __name__ == '__main__':
    unittest.main()
