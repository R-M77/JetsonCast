from pathlib import Path
import struct
import sys
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import privacy_check


def png_chunk(kind, payload):
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))


def png(*extra):
    return (b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + b''.join(extra) + png_chunk(b'IDAT', zlib.compress(b'\0\x12\x34\x56')) + png_chunk(b'IEND', b''))


GIF_HEADER = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff'
GIF_LOOP = b'\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00'
GIF_IMAGE = b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'


class PrivacyMetadataTests(unittest.TestCase):
    def test_png_accepts_display_parameters_and_rejects_provenance(self):
        display = png_chunk(b'pHYs', struct.pack('>IIB', 3780, 3780, 1))
        self.assertEqual(privacy_check.inspect('sample.png', png(display)), [])
        for chunk in (b'caBX', b'tEXt', b'iCCP', b'zzZZ'):
            with self.subTest(chunk=chunk):
                self.assertEqual(privacy_check.inspect('sample.png', png(png_chunk(chunk, b'fixture'))),
                                 ['image-metadata'])

    def test_png_validates_signature_chunk_checksum_and_end(self):
        image = png()
        self.assertEqual(privacy_check.inspect('sample.png', b'not an image'), ['invalid-PNG-signature'])
        self.assertEqual(privacy_check.inspect('sample.png', image[:-1]), ['truncated-PNG'])
        self.assertEqual(privacy_check.inspect('sample.png', image[:-1] + bytes([image[-1] ^ 1])),
                         ['invalid-PNG-checksum'])
        self.assertEqual(privacy_check.inspect('sample.png', image + b'fixture'), ['PNG-trailing-data'])

    def test_gif_accepts_exact_loop_and_rejects_other_metadata(self):
        self.assertEqual(privacy_check.inspect('sample.gif', GIF_HEADER + GIF_LOOP + GIF_IMAGE), [])
        self.assertEqual(privacy_check.inspect('sample.gif', GIF_HEADER + b'\x21\xfe\x01a\x00' + GIF_IMAGE),
                         ['GIF-comment-metadata'])
        extended_loop = GIF_LOOP[:-1] + b'\x01a\x00'
        self.assertEqual(privacy_check.inspect('sample.gif', GIF_HEADER + extended_loop + GIF_IMAGE),
                         ['GIF-application-metadata'])

    def test_gif_validates_signature_blocks_and_end(self):
        image = GIF_HEADER + GIF_IMAGE
        self.assertEqual(privacy_check.inspect('sample.gif', b'not an image'), ['invalid-GIF-signature'])
        self.assertEqual(privacy_check.inspect('sample.gif', GIF_HEADER + b'\x21'), ['truncated-GIF'])
        self.assertEqual(privacy_check.inspect('sample.gif', image[:-2]), ['truncated-GIF'])
        self.assertEqual(privacy_check.inspect('sample.gif', image + b'fixture'), ['GIF-trailing-data'])

    def test_commit_accepts_matching_github_identities_in_both_noreply_formats(self):
        fields = [
            'fixture-contributor', '12345+Fixture-Contributor@users.noreply.github.com',
            'fixture-maintainer', 'fixture-maintainer@users.noreply.github.com',
            '2026-01-01T12:00:00+00:00', '2026-01-01T12:00:00Z', 'Fixture message',
        ]
        self.assertEqual(privacy_check.commit_findings('\0'.join(fields)), [])

    def test_commit_rejects_nonmatching_or_non_noreply_identities(self):
        name = 'fixture-contributor'
        email = name + '@users.noreply.github.com'
        utc = '2026-01-01T12:00:00+00:00'
        fields = [name, email, name, email, utc, utc, 'Fixture message']
        invalid = [
            ('Fixture Display Name', email), (name, 'other-fixture@users.noreply.github.com'),
            (name, name + '@' + 'example.com'), (name, 'prefix+' + email),
            ('fixture--contributor', 'fixture--contributor@users.noreply.github.com'),
        ]
        for offset in (0, 2):
            for invalid_name, invalid_email in invalid:
                with self.subTest(offset=offset, name=invalid_name, email=invalid_email):
                    changed = fields.copy()
                    changed[offset:offset + 2] = [invalid_name, invalid_email]
                    self.assertEqual(privacy_check.commit_findings('\0'.join(changed)), ['unapproved-Git-identity'])

    def test_commit_requires_both_utc_offsets(self):
        name, email = 'R-M77', '88836105+R-M77@users.noreply.github.com'
        utc = '2026-01-01T12:00:00+00:00'
        fields = [name, email, name, email, utc, utc, 'Fixture message']
        self.assertEqual(privacy_check.commit_findings('\0'.join(fields)), [])
        for field in (4, 5):
            with self.subTest(field=field):
                changed = fields.copy()
                changed[field] = '2026-01-01T13:00:00+01:00'
                self.assertEqual(privacy_check.commit_findings('\0'.join(changed)), ['non-UTC-Git-timestamp'])


if __name__ == '__main__':
    unittest.main()
