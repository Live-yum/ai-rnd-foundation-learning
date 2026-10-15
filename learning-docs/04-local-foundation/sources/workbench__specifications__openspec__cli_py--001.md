# workbench/specifications/openspec/cli.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：终端入口和运维命令。** Typer把Python函数映射为rnd子命令。init建立本机数据和索引，start启动网页，chat/recommend调用与网页相同的API；index/tools等工具命令是独立的本机诊断入口。token只供本机使用，不应贴进公开日志。

**对应关系：** pyproject的project.scripts → cli.app → api/runtime/toolchain；test_tools_cli。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.infrastructure.processes.tools`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `OpenSpecCLI`（L16–L62）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `OpenSpecCLI.__init__`（L17–L22）：接收`workspace`、`executable`、`timeout`。 调用`Path(workspace).resolve`、`Path`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `OpenSpecCLI._run`（L24–L44）：接收`args`、`json_output`。 控制顺序：L26按`not node or not Path(self.executable).is_file()`分支；L27抛异常，停止当前正常路径；L38按`result.returncode`分支；L39抛异常，停止当前正常路径；L42按`len(raw) > 200000`分支；L43抛异常，停止当前正常路径。 调用`shutil.which`、`Path(self.executable).is_file`、`Path`、`ValueError`、`__import__("tempfile").TemporaryFile`、`__import__`、`subprocess.run`、`str`、`clean_env`等。 返回路径：L44的`json.loads(raw) if json_output else raw.decode().strip()`。
- `OpenSpecCLI.check_version`（L46–L48）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L47按`self._run(["--version"], json_output=False) != VERSION`分支；L48抛异常，停止当前正常路径。 调用`self._run`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `OpenSpecCLI.validate_schema`（L50–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self._run`。 返回路径：L51的`self._run(["schema", "validate", SCHEMA, "--json"])`。
- `OpenSpecCLI.new_change`（L53–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self._run`。 返回路径：L54的`self._run(["new", "change", "product", "--schema", SCHEMA, "--json"])`。
- `OpenSpecCLI.instructions`（L56–L59）：接收`artifact`。 控制顺序：L57按`artifact not in ARTIFACTS`分支；L58抛异常，停止当前正常路径。 调用`ValueError`、`self._run`。 返回路径：L59的`self._run(["instructions", artifact, "--change", "product", "--json"])`。
- `OpenSpecCLI.status`（L61–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self._run`。 返回路径：L62的`self._run(["status", "--change", "product", "--json"])`。

</details>

**创建路径：** `workbench/specifications/openspec/cli.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L62。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2397`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/specifications/openspec/cli.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2e18a21e4cf41c25990ef9d8d2de621e0dfa2a404336dd04676dc48d085102e8"} -->
````python
# workbench/specifications/openspec/cli.py
"""The only OpenSpec commands permitted by production are document operations."""

import json
import shutil
import subprocess
from pathlib import Path

from workbench.infrastructure.processes.tools import clean_env
from workbench.settings import ROOT

VERSION = "1.14.1"
SCHEMA = "rnd-factory"
ARTIFACTS = ("proposal", "specs", "design", "tasks")


class OpenSpecCLI:
    def __init__(self, workspace, *, executable=None, timeout=30):
        self.workspace = Path(workspace).resolve()
        self.timeout = timeout
        self.executable = (
            executable or ROOT / "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js"
        )

    def _run(self, args, *, json_output=True):
        node = shutil.which("node")
        if not node or not Path(self.executable).is_file():
            raise ValueError("OpenSpec pinned runtime missing; run npm ci --prefix tools/openspec")
        with __import__("tempfile").TemporaryFile() as output:
            result = subprocess.run(
                [node, str(self.executable), *args],
                cwd=self.workspace,
                env=clean_env({"OPENSPEC_TELEMETRY": "0", "DO_NOT_TRACK": "1", "CI": "1"}),
                stdout=output,
                stderr=subprocess.DEVNULL,
                timeout=self.timeout,
                check=False,
            )
            if result.returncode:
                raise ValueError("OpenSpec document command failed")
            output.seek(0)
            raw = output.read(200001)
        if len(raw) > 200000:
            raise ValueError("OpenSpec JSON exceeds budget")
        return json.loads(raw) if json_output else raw.decode().strip()

    def check_version(self):
        if self._run(["--version"], json_output=False) != VERSION:
            raise ValueError("OpenSpec version differs from reviewed lock")

    def validate_schema(self):
        return self._run(["schema", "validate", SCHEMA, "--json"])

    def new_change(self):
        return self._run(["new", "change", "product", "--schema", SCHEMA, "--json"])

    def instructions(self, artifact):
        if artifact not in ARTIFACTS:
            raise ValueError("Only proposal/specs/design/tasks instructions are allowed")
        return self._run(["instructions", artifact, "--change", "product", "--json"])

    def status(self):
        return self._run(["status", "--change", "product", "--json"])
````
