# tests/test_handbook_labs.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_all_expected_lessons_are_present`（L18–L19）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L19断言`[number for _, number in BLOCKS] == [f"{number:02d}" for number in range(7)]`。 调用`range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_lesson_runs_from_the_printed_code`（L23–L35）：接收`source`、`number`、`tmp_path`。 控制顺序：L35断言`result.returncode == 0`。 调用`path.write_text`、`subprocess.run`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_teaching_notes_do_not_confuse_same_named_functions`（L38–L46）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L43断言`"不联系Dex" in auth`；L44断言`"真实签发" not in auth`；L45断言`"可读DDL" in sql`；L46断言`"生成物完全由正文" not in sql`。 调用`notes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook_labs.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L46。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1499`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook_labs.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9a7ac624eddeee3d3d88d2b6b4cfd55b42ad590cb5c2cfdfc0fe461d50465024"} -->
````python
# tests/test_handbook_labs.py
"""Every complete teaching experiment must run as written, without network/model keys."""

import os
import re
import subprocess
import sys

import pytest

from scripts.build_handbook import ROOT

LESSON = ROOT / "docs/implementation-labs.md"
BLOCKS = re.findall(
    r"```python\n(# lesson: (\d+)\n.*?)\n```", LESSON.read_text(encoding="utf-8"), re.S
)


def test_all_expected_lessons_are_present():
    assert [number for _, number in BLOCKS] == [f"{number:02d}" for number in range(7)]


@pytest.mark.parametrize("source,number", BLOCKS, ids=[number for _, number in BLOCKS])
def test_complete_lesson_runs_from_the_printed_code(source, number, tmp_path):
    path = tmp_path / f"lesson_{number}.py"
    path.write_text(source + "\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_teaching_notes_do_not_confuse_same_named_functions():
    from scripts.handbook_notes import notes

    auth = notes("workbench/api.py", "def auth():\n    return None\n")
    sql = notes("workbench/product_sql.py", "def render():\n    return None\n")
    assert "不联系Dex" in auth
    assert "真实签发" not in auth
    assert "可读DDL" in sql
    assert "生成物完全由正文" not in sql
````
