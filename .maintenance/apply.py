"""Apply the four reviewed source diffs; this one-time helper is removed before final acceptance."""

from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
patches = [root / '.maintenance' / f'part{n}.patch' for n in range(1, 5)]
patch = ''.join(p.read_text(encoding='utf-8').replace('\n diff --git ', '\ndiff --git ') for p in patches)
subprocess.run(['git', 'apply', '--check', '-'], input=patch.encode(), cwd=root, check=True)
subprocess.run(['git', 'apply', '-'], input=patch.encode(), cwd=root, check=True)

def replace(name, old, new):
    path = root / name
    body = path.read_text(encoding='utf-8')
    if body.count(old) != 1:
        raise ValueError('Expected unique reviewed anchor: ' + name)
    path.write_text(body.replace(old, new), encoding='utf-8')

replace('scripts/daytona_matrix_probe.py', 'from workbench.tools import clean_env', 'from workbench.owned_lifecycle import stop_native\nfrom workbench.tools import clean_env')
replace('scripts/daytona_matrix_probe.py', '        stop_process(process); log.close()', '        try:\n            stop_native(process, [8001 if template == "fastapiadmin" else 48080, 5173])\n        finally:\n            log.close()')
replace('workbench/native_coding.py', '    literals = re.compile(', '    if suffix == ".java" and "\\\\u" in expression:\n        raise ValueError("Java Unicode escapes cannot bypass the expression lexer")\n    literals = re.compile(')
path = root / 'tests/test_native_tools.py'
with path.open('a', encoding='utf-8') as out:
    out.write('\n\ndef test_java_unicode_escape_cannot_bypass_expression_lexer():\n    with pytest.raises(ValueError, match="Unicode"):\n        validate_expression(chr(34) + chr(92) + "u0061" + chr(34) + ".equals(" + chr(34) + "a" + chr(34) + ")", ".java", [])\n')
print('Reviewed integration diffs applied; dependencies and handbook must be regenerated and tested next.')
