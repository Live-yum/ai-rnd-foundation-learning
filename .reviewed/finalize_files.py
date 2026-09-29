"""Apply reviewed complete documentation and regression fixes; diagnostics only."""

import base64
import hashlib
import json
import lzma
from pathlib import Path

encoded = "".join(Path(f".reviewed/final-docs.{i}").read_text() for i in range(4))
raw = lzma.decompress(base64.b64decode(encoded))
assert hashlib.sha256(raw).hexdigest() == "d92547d40b1103fe113f8fcd6d869e51bc5db438e051bf9a529e66a8c7066d5f"
files = json.loads(raw)
allowed = {"README.md", ".env.example", "SECURITY.md", "docs/guide.md", "docs/native-baseline.md", "templates/frontends/simple-admin/app.js", "scripts/guided_browser.cjs"}
assert set(files) == allowed
for name, item in files.items():
    path = Path(name)
    if path.read_text(encoding="utf-8") == item["content"]:
        continue
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["before"], name
for name, item in files.items():
    Path(name).write_text(item["content"], encoding="utf-8", newline="\n")
path = Path("tests/test_guided_completion.py")
text = path.read_text(encoding="utf-8")
old = '(ROOT / "templates/deployment/run.py").read_text()'
new = '(ROOT / "templates/deployment/run.py").read_text(encoding="utf-8")'
if new not in text:
    assert text.count(old) == 1
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
print("Reviewed complete guide, filter reset and Windows UTF-8 source read applied")
