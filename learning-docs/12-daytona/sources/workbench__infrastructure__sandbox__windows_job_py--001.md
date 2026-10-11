# workbench/infrastructure/sandbox/windows_job.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.errors`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `BasicLimits`（L9–L20）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `IOCounters`（L23–L34）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ExtendedLimits`（L37–L45）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `WindowsJob`（L48–L88）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `WindowsJob.__init__`（L49–L78）：接收`process`、`api`。 控制顺序：L61遍历`signatures.items()`；L65按`not self.handle`分支；L66抛异常，停止当前正常路径；L70按`not self.api.SetInformationJobObject( self.handle, 9, ctypes.byref(limits), ctypes.si…`分支；L73抛异常，停止当前正常路径；L74按`not self.api.AssignProcessToJobObject(self.handle, int(process._handle))`分支；L75抛异常，停止当前正常路径；L78抛异常，停止当前正常路径。 调用`ctypes.WinDLL`、`signatures.items`、`getattr`、`self.api.CreateJobObjectW`、`UnsupportedScope`、`ExtendedLimits`、`self.api.SetInformationJobObject`、`ctypes.byref`、`ctypes.sizeof`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `WindowsJob.terminate`（L80–L82）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L81按`not self.api.TerminateJobObject(self.handle, 1)`分支；L82抛异常，停止当前正常路径。 调用`self.api.TerminateJobObject`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `WindowsJob.close`（L84–L88）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85按`self.handle`分支；L87按`not self.api.CloseHandle(handle)`分支；L88抛异常，停止当前正常路径。 调用`self.api.CloseHandle`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/infrastructure/sandbox/windows_job.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L88。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3397`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/sandbox/windows_job.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ab9a78c0975f66390262b39de147d11d5f4a636636f334817692167f84c4c6cd"} -->
````python
# workbench/infrastructure/sandbox/windows_job.py
"""An owned Windows job, assigned before the trusted SDK child receives work."""

import ctypes
from ctypes import wintypes

from workbench.errors import UnsupportedScope


class BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]


class IOCounters(ctypes.Structure):
    _fields_ = [
        (key, ctypes.c_ulonglong)
        for key in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", BasicLimits),
        ("IoInfo", IOCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class WindowsJob:
    def __init__(self, process, *, api=None):
        self.api = api if api is not None else ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32],
                ctypes.c_int32,
            ),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], ctypes.c_int32),
            "TerminateJobObject": ([wintypes.HANDLE, ctypes.c_uint32], ctypes.c_int32),
            "CloseHandle": ([wintypes.HANDLE], ctypes.c_int32),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise UnsupportedScope("Windows file worker job creation failed")
        try:
            limits = ExtendedLimits()
            limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.api.SetInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
            ):
                raise UnsupportedScope("Windows file worker job configuration failed")
            if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
                raise UnsupportedScope("Windows file worker job assignment failed")
        except BaseException:
            self.close()
            raise

    def terminate(self):
        if not self.api.TerminateJobObject(self.handle, 1):
            raise UnsupportedScope("Windows file worker subtree termination failed")

    def close(self):
        if self.handle:
            handle, self.handle = self.handle, None
            if not self.api.CloseHandle(handle):
                raise UnsupportedScope("Windows file worker job handle closure failed")
````
