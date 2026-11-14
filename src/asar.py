"""Small ASAR reader/repacker for the pinned, packed-only upstream release.

No extraction to arbitrary paths. Rejects links/unpacked entries and recomputes
Electron integrity metadata for modified files. Format: Chromium Pickle header.
"""
import hashlib
import json
import struct


def read(blob):
    if len(blob) < 16:
        raise ValueError('Truncated ASAR')
    size_size, header_size, payload_size, json_size = struct.unpack('<4I', blob[:16])
    if size_size != 4 or payload_size + 4 != header_size or json_size > payload_size - 4:
        raise ValueError('Invalid ASAR header')
    start = 8 + header_size
    if start > len(blob):
        raise ValueError('Truncated ASAR header')
    header = json.loads(blob[16:16 + json_size])
    files = {}

    def walk(tree, prefix=''):
        for name, item in tree.items():
            if name in ('.', '..') or '/' in name or '\\' in name:
                raise ValueError('Unsafe ASAR filename')
            full = prefix + name
            if 'files' in item:
                walk(item['files'], full + '/')
            else:
                if item.get('unpacked') or 'link' in item:
                    raise ValueError('Unsupported ASAR link/unpacked entry')
                offset, size = int(item['offset']), int(item['size'])
                if offset < 0 or size < 0 or start + offset + size > len(blob):
                    raise ValueError('Invalid ASAR file bounds')
                files[full] = (blob[start + offset:start + offset + size], bool(item.get('executable')))
    walk(header['files'])
    return files


def pack(files):
    root = {'files': {}}
    chunks, offset = [], 0
    for name, (data, executable) in sorted(files.items()):
        node = root
        parts = name.split('/')
        if any(p in ('', '.', '..') or '\\' in p for p in parts):
            raise ValueError('Unsafe ASAR filename')
        for part in parts[:-1]:
            node = node['files'].setdefault(part, {'files': {}})
        block_size = 4194304
        entry = {'size': len(data), 'offset': str(offset), 'integrity': {
            'algorithm': 'SHA256', 'hash': hashlib.sha256(data).hexdigest(),
            'blockSize': block_size,
            'blocks': [hashlib.sha256(data[i:i+block_size]).hexdigest()
                       for i in range(0, len(data), block_size)]}}
        if executable:
            entry['executable'] = True
        node['files'][parts[-1]] = entry
        chunks.append(data)
        offset += len(data)
    raw = json.dumps(root, separators=(',', ':'), ensure_ascii=False).encode()
    payload = struct.pack('<I', len(raw)) + raw
    payload += b'\0' * (-len(payload) % 4)
    header = struct.pack('<I', len(payload)) + payload
    return struct.pack('<II', 4, len(header)) + header + b''.join(chunks)
