# workbench/infrastructure/sandbox/coding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：不依赖Aider的受限规则编辑。** apply_patch只接收允许文件的替换内容，校验旧内容和新规则。code_rules向网关请求结构化补丁并保存每轮证据。它不执行任意shell，也不能越权修改认证、路由和依赖锁。

**对应关系：** flow → coding → ModelGateway + Rules → verification；test_safety。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_execution`、`workbench.capability_isolation`、`workbench.coding.candidates`、`workbench.errors`、`workbench.filesystem`、`workbench.sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `DaytonaFiles`（L24–L60）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DaytonaFiles.__init__`（L25–L27）：接收`sandbox`、`task`、`timeout`、`deadline`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DaytonaFiles.remaining`（L29–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L36按`remaining <= 0`分支；L37抛异常，停止当前正常路径。 调用`min`、`time.monotonic`、`int`、`UnsupportedScope`。 返回路径：L38的`remaining`。
- `DaytonaFiles.write`（L40–L47）：接收`edits`。 控制顺序：L41按`{edit.path for edit in edits.files} != set(self.task.allowed_paths)`分支；L42抛异常，停止当前正常路径；L43遍历`edits.files`。 调用`set`、`ValueError`、`self.remaining`、`self.sandbox.fs.create_folder`、`remote.rsplit`、`self.sandbox.fs.upload_file`、`edit.content.encode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DaytonaFiles.snapshot`（L49–L60）：接收`paths`。 控制顺序：L50按`paths != self.task.allowed_paths`分支；L51抛异常，停止当前正常路径；L53遍历`paths`；L57按`not isinstance(content, bytes) or len(content) > 100000`分支；L58抛异常，停止当前正常路径。 调用`ValueError`、`self.sandbox.fs.download_file`、`self.remaining`、`isinstance`、`len`、`content.decode`。 返回路径：L60的`result`。
- `coding_environment`（L64–L137）：接收`settings`、`task`、`selection`、`product`、`deadline`。 控制顺序：L69按`task_path_errors(task, selection)`分支；L70抛异常，停止当前正常路径；L104按`sandbox.network_block_all is not True or sandbox.public is not False`分支；L105抛异常，停止当前正常路径；L134按`sandbox is not None`分支。 调用`task_path_errors`、`UnsupportedScope`、`capability_execution_prerequisites`、`client_for`、`_DEADLINE.set`、`client.create`、`params_for`、`uuid.uuid4`、`remaining`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `coding_environment.remaining`（L76–L90）：接收`cleanup`。 控制顺序：L84按`available <= 0`分支；L85按`cleanup`分支；L89抛异常，停止当前正常路径。 调用`min`、`time.monotonic`、`int`、`UnsupportedScope`。 返回路径：L88的`1`；L90的`available`。

</details>

**创建路径：** `workbench/infrastructure/sandbox/coding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L137。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5470`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/coding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ab1f57739484f7f68692c618d2a15b1998d4426ed914eb7271aede213dc984ed"} -->
````python
# workbench/infrastructure/sandbox/coding.py
"""File-only coding session on the existing admitted private Daytona channel.

No agent command is executed, even inside the container. Generated code is run
later exclusively by the independent capability verifier.
"""

import time
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
    def __init__(self, sandbox, task, timeout, deadline=None):
        self.sandbox, self.task, self.timeout = sandbox, task, timeout
        self.deadline = deadline

    def remaining(self):
        remaining = (
            self.timeout
            if self.deadline is None
            else min(self.timeout, self.deadline - time.monotonic())
        )
        remaining = int(remaining)
        if remaining <= 0:
            raise UnsupportedScope("Agent filesystem deadline exhausted")
        return remaining

    def write(self, edits):
        if {edit.path for edit in edits.files} != set(self.task.allowed_paths):
            raise ValueError("Agent files differ from approved paths")
        for edit in edits.files:
            self.remaining()
            remote = REMOTE + "/" + edit.path
            self.sandbox.fs.create_folder(remote.rsplit("/", 1)[0], "700")
            self.sandbox.fs.upload_file(edit.content.encode(), remote, timeout=self.remaining())

    def snapshot(self, paths):
        if paths != self.task.allowed_paths:
            raise ValueError("snapshot paths differ from task")
        result = {}
        for name in paths:
            # SDK 0.190.0 overloads advertise timeout=, but its implementation
            # accepts only positional arguments. Keep empty-file support too.
            content = self.sandbox.fs.download_file(REMOTE + "/" + name, self.remaining())
            if not isinstance(content, bytes) or len(content) > 100000:
                raise ValueError("sandbox file exceeds source budget")
            result[name] = content.decode("utf-8")
        return result


@contextmanager
def coding_environment(settings, task, selection, product, *, deadline=None):
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.daytona_sessions import _DEADLINE
    from workbench.planning.contracts import CapabilityEdits, SourceEdit

    if task_path_errors(task, selection):
        raise UnsupportedScope("Agent task crosses the business-file boundary")
    directory, profile = capability_execution_prerequisites(settings, selection)
    client = client_for(settings)
    sandbox = None
    token = _DEADLINE.set(None if deadline is None else deadline - 15)

    def remaining(cleanup=False):
        end = deadline if cleanup or deadline is None else deadline - 15
        available = (
            settings.tool_timeout
            if end is None
            else min(settings.tool_timeout, end - time.monotonic())
        )
        available = int(available)
        if available <= 0:
            if cleanup:
                # Never skip owned cleanup when an SDK call overruns. The caller
                # rejects any result after the module deadline, even if deletion succeeds.
                return 1
            raise UnsupportedScope("Agent sandbox deadline exhausted")
        return available

    try:
        # The admitted Runner selects strict network/resource limits by this
        # existing source prefix, shared with the independent verifier.
        prefix = "rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-"
        sandbox = client.create(
            params_for(
                settings, prefix + "agent-" + uuid.uuid4().hex, selection["template"], selection
            ),
            timeout=remaining(),
        )
        remaining()
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
        env = DaytonaFiles(
            sandbox, task, settings.tool_timeout, None if deadline is None else deadline - 15
        )
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
            _DEADLINE.reset(token)
            if sandbox is not None:
                client.delete(sandbox, timeout=remaining(cleanup=True))
        finally:
            close_client(client)
````
