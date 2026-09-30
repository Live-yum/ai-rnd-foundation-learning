"""One-time exact-source importer, removed before formal testing or delivery."""
import ast
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path.cwd()
patch_files = [ROOT / '.maintenance' / (name + '.py') for name in ('context', 'editor', 'tests', 'docs')]
prepared = {}
for patch_file in patch_files:
    module = ast.parse(patch_file.read_text(encoding='utf-8'))
    if len(module.body) != 1 or not isinstance(module.body[0], ast.Assign):
        raise ValueError('Source patch must contain only literal data')
    patches = ast.literal_eval(module.body[0].value)
    for name, (expected, edits) in patches.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or name.startswith(('.github/', '.maintenance/')) or name in prepared:
            raise ValueError('Invalid or duplicate source path: ' + name)
        target = ROOT / name
        original = target.read_bytes() if target.exists() else b''
        if hashlib.sha256(original).hexdigest() != expected:
            raise ValueError('Reviewed preimage changed: ' + name)
        lines = original.decode('utf-8').splitlines(keepends=True)
        last = len(lines)
        for first, end, replacement in reversed(edits):
            if not 0 <= first <= end <= last:
                raise ValueError('Invalid patch interval: ' + name)
            lines[first:end] = replacement.splitlines(keepends=True)
            last = first
        prepared[name] = ''.join(lines).encode('utf-8')

# Download only the two exact reviewed public source blobs. Runtime never downloads them.
manifest = json.loads(prepared['tools/node/upstream/manifest.json'])
revision = '5522c6f44ca0ac3528b37244818fbfa39b5af470'
if manifest['revision'] != revision:
    raise ValueError('Unexpected Continue revision')
for name, expected in manifest['files'].items():
    if name not in {'LICENSE', 'FullTextSearchCodebaseIndex.ts'}:
        raise ValueError('Unexpected upstream file')
    url = 'https://raw.githubusercontent.com/continuedev/continue/' + revision + '/' + expected['path']
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read(200001)
    if len(data) > 200000 or hashlib.sha256(data).hexdigest() != expected['sha256']:
        raise ValueError('Pinned source SHA256 mismatch: ' + name)
    git_blob = hashlib.sha1(('blob ' + str(len(data)) + '\0').encode() + data).hexdigest()
    if git_blob != expected['git_blob_sha1']:
        raise ValueError('Pinned source Git blob mismatch: ' + name)
    data.decode('utf-8')
    prepared['tools/node/upstream/' + name] = data

for name, content in prepared.items():
    target = ROOT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
subprocess.run(['git', 'add', '--', *prepared], check=True, timeout=60)
for patch_file in patch_files:
    patch_file.unlink()
Path(__file__).unlink()
print('Imported', len(prepared), 'SHA-checked source files; no production data or credentials touched.')
