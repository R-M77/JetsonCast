#!/usr/bin/env python3
"""Fail closed on likely private data in tracked files and optional Git history.

This is a publication guard, not a proof of absence of every possible secret.
Only filenames/rule names are printed; matching content is never echoed.
"""
import argparse
import hashlib
import ipaddress
from pathlib import Path
import re
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
GITHUB_NOREPLY = re.compile(r'(?:[0-9]+\+)?(?P<username>[a-z0-9]+(?:-[a-z0-9]+)*)@users\.noreply\.github\.com',
                            re.ASCII | re.IGNORECASE)
COMMIT_FIELDS = '%an%x00%ae%x00%cn%x00%ce%x00%aI%x00%cI%x00%B'
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
# Keep image data and fixed-size display parameters. Exclude provenance, comments,
# arbitrary color profiles, and other chunks that can carry embedded documents.
PNG_CHUNKS = {
    b'IHDR': (13,), b'PLTE': range(3, 769, 3), b'IDAT': None, b'IEND': (0,),
    b'tRNS': range(1, 257), b'bKGD': (1, 2, 6), b'cHRM': (32,), b'gAMA': (4,),
    b'pHYs': (9,), b'sBIT': (1, 2, 3, 4), b'sRGB': (1,),
}
GIF_SIGNATURES = (b'GIF87a', b'GIF89a')
# Use repository-relative POSIX paths. Keep reviewed hashes for reachable history.
REVIEWED_PREVIEW_MP4S = {
    'assets/previews/demo-landscape.mp4': {
        '8822904708200ab6f9366edfc4d96de3f58a7c7ae273cfbd2f57dcd089f7b48c',
        '2648597594dc6c437c6ae381245575d6e52520f0775dfb89360893298965447a',
    },
    'assets/previews/demo-vertical.mp4': {
        'c8ca83047129848a29b575dfa8dcb4dad91f387dd0266352498a347f61d6b135',
        'd645bb25145f3fa9875896a5d374a4215415ad494e07cb042a96ce71d81ec46b',
    },
}
RULES = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'access-token': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{32,}|AKIA[0-9A-Z]{16})'),
    'personal-home-path': re.compile(r'(?:[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\s"\']+|/' + r'home/[^/\s"\']+/|/' + r'Users/[^/\s"\']+/)', re.I),
    'hardware-address': re.compile(r'\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b', re.I),
    'credential-url': re.compile(r'https?://[^\s/]+:[^\s/]+@'),
}
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
IP = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def text_findings(text):
    found = [name for name, pattern in RULES.items() if pattern.search(text)]
    for email in EMAIL.findall(text):
        if not email.endswith('@users.noreply.github.com'):
            found.append('non-GitHub-email')
    for address in IP.findall(text):
        try:
            ip = ipaddress.IPv4Address(address)
        except ValueError:
            continue  # version strings are not IP addresses
        if any(ip in ipaddress.IPv4Network(net) for net in ((0x0a000000, 8), (0xac100000, 12), (0xc0a80000, 16))):
            found.append('private-LAN-address')
    return sorted(set(found))


def matches_github_identity(name, email):
    match = GITHUB_NOREPLY.fullmatch(email)
    return bool(match and len(name) <= 39 and name.isascii() and name.lower() == match['username'].lower())


def commit_findings(metadata):
    author, author_email, committer, committer_email, author_date, committer_date, message = metadata.split('\0', 6)
    findings = text_findings(message)
    if not matches_github_identity(author, author_email) or not matches_github_identity(committer, committer_email):
        findings.append('unapproved-Git-identity')
    if not author_date.endswith(('+00:00', 'Z')) or not committer_date.endswith(('+00:00', 'Z')):
        findings.append('non-UTC-Git-timestamp')
    return findings


def png_findings(data):
    if not data.startswith(PNG_SIGNATURE):
        return ['invalid-PNG-signature']
    offset = len(PNG_SIGNATURE)
    previous = None
    seen = set()
    has_data = False
    view = memoryview(data)
    while offset + 12 <= len(data):
        size, kind = struct.unpack_from('>I4s', data, offset)
        crc_offset = offset + 8 + size
        end = crc_offset + 4
        if end > len(data):
            return ['truncated-PNG']
        if zlib.crc32(view[offset + 4:crc_offset]) != struct.unpack_from('>I', data, crc_offset)[0]:
            return ['invalid-PNG-checksum']
        if kind not in PNG_CHUNKS:
            return ['image-metadata']
        sizes = PNG_CHUNKS[kind]
        if sizes is not None and (size not in sizes or kind in seen):
            return ['invalid-PNG-structure']
        if kind == b'IHDR':
            if previous is not None or not all(struct.unpack_from('>II', data, offset + 8)):
                return ['invalid-PNG-structure']
        elif previous is None:
            return ['invalid-PNG-structure']
        elif kind == b'IDAT':
            if kind in seen and previous != b'IDAT':
                return ['invalid-PNG-structure']
            has_data |= size > 0
        elif kind == b'IEND':
            if not has_data:
                return ['invalid-PNG-structure']
            return [] if end == len(data) else ['PNG-trailing-data']
        seen.add(kind)
        previous = kind
        offset = end
    return ['truncated-PNG']


def gif_color_table_size(flags):
    return 3 * (2 ** ((flags & 7) + 1)) if flags & 128 else 0


def gif_sub_blocks_end(data, offset):
    while offset < len(data):
        size = data[offset]
        offset += 1
        if not size:
            return offset
        offset += size
    return None


def gif_findings(data):
    if data[:6] not in GIF_SIGNATURES:
        return ['invalid-GIF-signature']
    if len(data) < 13:
        return ['truncated-GIF']
    screen_width, screen_height, flags = struct.unpack_from('<HHB', data, 6)
    if not screen_width or not screen_height:
        return ['invalid-GIF-structure']
    global_table = gif_color_table_size(flags)
    offset = 13 + global_table
    has_image = False
    while offset < len(data):
        tag = data[offset]
        if tag == 0x3b:
            if not has_image:
                return ['invalid-GIF-structure']
            return [] if offset + 1 == len(data) else ['GIF-trailing-data']
        if tag == 0x21:
            if offset + 2 > len(data):
                return ['truncated-GIF']
            kind = data[offset + 1]
            if kind == 0xfe:
                return ['GIF-comment-metadata']
            if kind == 0xff:
                loop = data[offset + 2:offset + 19]
                if (len(loop) != 17 or loop[:14] != b'\x0bNETSCAPE2.0\x03\x01' or loop[-1] != 0):
                    return ['GIF-application-metadata']
                offset += 19
            elif kind == 0xf9:
                if offset + 8 > len(data):
                    return ['truncated-GIF']
                if data[offset + 2] != 4 or data[offset + 7] != 0:
                    return ['invalid-GIF-structure']
                offset += 8
            else:
                return ['GIF-extension-metadata']
        elif tag == 0x2c:
            if offset + 10 > len(data):
                return ['truncated-GIF']
            left, top, width, height, flags = struct.unpack_from('<HHHHB', data, offset + 1)
            local_table = gif_color_table_size(flags)
            if (not width or not height or left + width > screen_width or top + height > screen_height
                    or not (global_table or local_table)):
                return ['invalid-GIF-structure']
            offset += 10 + local_table
            if offset + 2 > len(data):
                return ['truncated-GIF']
            if not 2 <= data[offset] <= 8 or not data[offset + 1]:
                return ['invalid-GIF-structure']
            offset = gif_sub_blocks_end(data, offset + 1)
            if offset is None:
                return ['truncated-GIF']
            has_image = True
        else:
            return ['invalid-GIF-structure']
    return ['truncated-GIF']


def media_findings(data, suffix=''):
    if suffix == '.png' or data.startswith(PNG_SIGNATURE):
        return png_findings(data)
    if suffix == '.gif' or data[:6] in GIF_SIGNATURES:
        return gif_findings(data)
    return []


def inspect(name, data):
    path = Path(name)
    suffix = path.suffix.lower()
    findings = media_findings(data, suffix)
    if suffix == '.mp4' or data[4:8] == b'ftyp':
        reviewed = REVIEWED_PREVIEW_MP4S.get(name, ())
        if (suffix != '.mp4' or path.parent != Path('assets/previews')
                or not reviewed or hashlib.sha256(data).hexdigest() not in reviewed):
            findings.append('unreviewed-MP4')
    elif suffix not in ('.png', '.gif'):
        try:
            findings += text_findings(data.decode('utf-8'))
        except UnicodeDecodeError:
            findings.append('unreviewed-binary')
    if any(part in ('profile', 'state', '.ssh', 'node_modules', '__pycache__') for part in path.parts):
        findings.append('private-or-generated-directory')
    if path.name in ('settings.json', 'config.json', '.env'):
        findings.append('runtime-configuration')
    return sorted(set(findings))


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    failures = []
    names = git('ls-files', '-z').decode().split('\0')
    for name in filter(None, names):
        for rule in inspect(name, (ROOT / name).read_bytes()):
            failures.append((name, rule))
        for rule in inspect(name, git('show', ':' + name)):
            failures.append((name + ' (index)', rule))
    if args.history:
        for commit in git('rev-list', '--all').decode().splitlines():
            metadata = git('show', '-s', '--format=' + COMMIT_FIELDS, commit).decode()
            for rule in commit_findings(metadata):
                failures.append(('commit metadata', rule))
            for row in git('ls-tree', '-r', commit).decode().splitlines():
                metadata, name = row.split('\t', 1)
                _, kind, oid = metadata.split()
                if kind != 'blob':
                    continue
                for rule in inspect(name, git('cat-file', 'blob', oid)):
                    failures.append((name + ' (history)', rule))
    for name, rule in sorted(set(failures)):
        print('FAIL:', name, '[' + rule + ']')
    print('Privacy guard:', 'FAIL' if failures else 'PASS', '— review files and metadata before publication.')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
