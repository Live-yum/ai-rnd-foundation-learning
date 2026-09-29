"""Verify actual fixed upstream commits and indexes; this is NOT native runtime acceptance."""

import json

from workbench.native import prepare_sources
from workbench.settings import ROOT, Settings

settings = Settings(data_dir=ROOT / ".data" / "ci-native", tool_timeout=600, _env_file=None)
results = {
    template: prepare_sources(settings, template, prefer_github=True)
    for template in ("fastapiadmin", "yudao-vben")
}
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/native-sources.json").write_text(
    json.dumps(
        {
            "scope": "pinned-source-and-index-only",
            "runtime_verified": False,
            "sources": results,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(
    "PASS: fixed source commits, required paths, clean checkout and local index; not runtime certification"
)
