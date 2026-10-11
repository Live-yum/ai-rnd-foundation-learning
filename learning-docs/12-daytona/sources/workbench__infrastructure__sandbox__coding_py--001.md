# workbench/infrastructure/sandbox/coding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：不依赖Aider的受限规则编辑。** apply_patch只接收允许文件的替换内容，校验旧内容和新规则。code_rules向网关请求结构化补丁并保存每轮证据。它不执行任意shell，也不能越权修改认证、路由和依赖锁。

**对应关系：** flow → coding → ModelGateway + Rules → verification；test_safety。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_execution`、`workbench.capability_isolation`、`workbench.coding.candidates`、`workbench.errors`、`workbench.filesystem`、`workbench.sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `DaytonaFiles`（L23–L44）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DaytonaFiles.__init__`（L24–L25）：接收`sandbox`、`task`、`timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DaytonaFiles.write`（L27–L33）：接收`edits`。 控制顺序：L28按`{edit.path for edit in edits.files} != set(self.task.allowed_paths)`分支；L29抛异常，停止当前正常路径；L30遍历`edits.files`。 调用`set`、`ValueError`、`self.sandbox.fs.create_folder`、`remote.rsplit`、`self.sandbox.fs.upload_file`、`edit.content.encode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DaytonaFiles.snapshot`（L35–L44）：接收`paths`。 控制顺序：L36按`paths != self.task.allowed_paths`分支；L37抛异常，停止当前正常路径；L39遍历`paths`；L41按`not isinstance(content, bytes) or len(content) > 100000`分支；L42抛异常，停止当前正常路径。 调用`ValueError`、`self.sandbox.fs.download_file`、`isinstance`、`len`、`content.decode`。 返回路径：L44的`result`。
- `coding_environment`（L48–L98）：接收`settings`、`task`、`selection`、`product`。 控制顺序：L52按`task_path_errors(task, selection)`分支；L53抛异常，停止当前正常路径；L68按`sandbox.network_block_all is not True or sandbox.public is not False`分支；L69抛异常，停止当前正常路径；L95按`sandbox is not None`分支。 调用`task_path_errors`、`UnsupportedScope`、`capability_execution_prerequisites`、`client_for`、`client.create`、`params_for`、`uuid.uuid4`、`sandbox.refresh_data`、`require_container_evidence`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/infrastructure/sandbox/coding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L98。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3969`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/coding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "54b38fe97f1a721ca93328f81c6dd3415548b5b41a342be18e0e7764750b3d73"} -->
````python
# workbench/infrastructure/sandbox/coding.py
"""File-only coding session on the existing admitted private Daytona channel.

No agent command is executed, even inside the container. Generated code is run
later exclusively by the independent capability verifier.
"""

import uuid
from contextlib import contextmanager

from workbench.capability_execution import (
    capability_execution_prerequisites,
    require_profile_container_binding,
)
from workbench.capability_isolation import require_container_evidence
from workbench.coding.candidates import task_path_errors
from workbench.errors import UnsupportedScope
from workbench.filesystem import inside
from workbench.sandbox import client_for, close_client, params_for

REMOTE = "/tmp/rnd-agent-business"


class DaytonaFiles:
    def __init__(self, sandbox, task, timeout):
        self.sandbox, self.task, self.timeout = sandbox, task, timeout

    def write(self, edits):
        if {edit.path for edit in edits.files} != set(self.task.allowed_paths):
            raise ValueError("Agent files differ from approved paths")
        for edit in edits.files:
            remote = REMOTE + "/" + edit.path
            self.sandbox.fs.create_folder(remote.rsplit("/", 1)[0], "700")
            self.sandbox.fs.upload_file(edit.content.encode(), remote, timeout=self.timeout)

    def snapshot(self, paths):
        if paths != self.task.allowed_paths:
            raise ValueError("snapshot paths differ from task")
        result = {}
        for name in paths:
            content = self.sandbox.fs.download_file(REMOTE + "/" + name, timeout=self.timeout)
            if not isinstance(content, bytes) or len(content) > 100000:
                raise ValueError("sandbox file exceeds source budget")
            result[name] = content.decode("utf-8")
        return result


@contextmanager
def coding_environment(settings, task, selection, product):
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.planning.contracts import CapabilityEdits, SourceEdit

    if task_path_errors(task, selection):
        raise UnsupportedScope("Agent task crosses the business-file boundary")
    directory, profile = capability_execution_prerequisites(settings, selection)
    client = client_for(settings)
    sandbox = None
    try:
        # The admitted Runner selects strict network/resource limits by this
        # existing source prefix, shared with the independent verifier.
        prefix = "rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-"
        sandbox = client.create(
            params_for(
                settings, prefix + "agent-" + uuid.uuid4().hex, selection["template"], selection
            ),
            timeout=settings.tool_timeout,
        )
        sandbox.refresh_data()
        if sandbox.network_block_all is not True or sandbox.public is not False:
            raise UnsupportedScope("Agent sandbox is not private and network-blocked")
        evidence = require_container_evidence(
            inspect_created_sandbox(
                directory, sandbox.id, require_resources=True, selection=selection
            ),
            sandbox.id,
        )
        require_profile_container_binding(profile, evidence)
        env = DaytonaFiles(sandbox, task, settings.tool_timeout)
        env.write(
            CapabilityEdits(
                explanation="Approved before-images",
                files=[
                    SourceEdit(
                        path=name,
                        content=inside(product, name).read_bytes().decode("utf-8")
                        if inside(product, name).is_file()
                        else "",
                    )
                    for name in task.allowed_paths
                ],
            )
        )
        yield env
    finally:
        try:
            if sandbox is not None:
                client.delete(sandbox, timeout=settings.tool_timeout)
        finally:
            close_client(client)
````
