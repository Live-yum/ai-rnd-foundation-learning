"""Use the native visible label; preserve actual checked and HTTP value assertions."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}


def edit(name, old, new):
    source = changes.get(name, (root / name).read_text(encoding="utf-8"))
    if source.count(old) != 1:
        raise ValueError("Reviewed context changed: " + name)
    changes[name] = source.replace(old, new)


edit("scripts/native_browser.cjs", "            await dialog.getByRole('radio', { name: '否', exact: true }).nth(booleanIndex++).check();", "            const radio = dialog.getByRole('radio', { name: '否', exact: true }).nth(booleanIndex++);\n            // Ant Design hides its input; users interact with the enclosing visible label.\n            await radio.locator('xpath=ancestor::label[1]').click();\n            assert(await radio.isChecked(), 'Native boolean option was not selected');")
edit("docs/native-baseline.md", "| 5 | `workbench/native_frontend.py`、`scripts/native_browser.cjs` |", "| 5 | `workbench/native_vben.py`、`workbench/native_frontend.py`、`scripts/native_browser.cjs` |")
edit("docs/native-baseline.md", "tests/test_native_frontend_lifecycle.py -q", "tests/test_native_frontend_lifecycle.py tests/test_native_vben.py -q")
edit("docs/native-baseline.md", "| `browser.json`、`device.png`、`category.png` | 真实登录、真实列表请求、页面渲染与截图 |", "| `browser.json`、`device.png`、`category.png`、Vben 的 `device-created.png` / `category-created.png` | 真实登录、列表渲染、生成表单提交与截图 |")
edit("docs/native-baseline.md", "浏览器失败：读 `browser.json` 的响应、状态和page_errors，再看截图。", "浏览器失败：读 `browser.json` 的响应、状态和page_errors，再看截图。Ant Design 单选按钮内部 input 是隐藏的，真实自动操作点击对应可见 label，再验证 isChecked 和请求中的布尔值，不强制点击隐藏元素。")
for name, content in changes.items():
    (root / name).write_text(content, encoding="utf-8", newline="\n")
print("Updated native visible-label interaction and complete handbook instructions")
