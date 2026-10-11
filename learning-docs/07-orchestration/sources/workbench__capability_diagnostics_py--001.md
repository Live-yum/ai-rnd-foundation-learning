# workbench/capability_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_read`（L53–L62）：接收`path`。 控制顺序：L57按`len(raw) > 1_000_000`分支。 调用`Path(path).open`、`Path`、`source.read`、`len`、`json.loads`、`type`。 返回路径：L58的`{}`；L60的`result if type(result) is dict else {}`；L62的`{}`。
- `_label`（L65–L66）：接收`value`、`allowed`。 调用`type`。 返回路径：L66的`value if type(value) is str and value in allowed else "other"`。
- `record_failure`（L69–L84）：接收`receipt_path`、`exc`。 源码说明：Write a separate diagnostic; never add fields to the acceptance receipt.。 控制顺序：L77在`frame is not None`成立时循环；L79按`stage is not None`分支。 调用`_label`、`type`、`str`、`STAGES.items`、`trusted.get`、`failure.update`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `startup_diagnostic`（L87–L152）：接收`value`。 源码说明：Re-filter existing startup facts; output hints never establish acceptance.。 控制顺序：L89按`type(value) is not dict`分支；L98遍历`enums.items()`；L100遍历`(("http_status", 100, 599), ("command_exit_code", 0, 255))`；L103遍历`( "application_startup_reported", "output_readable", "output_none…`；L150按`type(target) is dict`分支。 调用`type`、`enums.items`、`_label`、`value.get`、`target.get`。 返回路径：L90的`None`；L152的`result`。
- `node_diagnostic`（L155–L187）：接收`product`、`aggregate`。 控制顺序：L164按`sidecar.stat().st_mtime_ns < path.stat().st_mtime_ns`分支；L177按`type(line) is int and 0 < line < 1_000_000`分支；L179遍历`("checks", "obligation_checks", "browser")`；L182遍历`("restarted", "backend_health_observed")`；L185按`startup is not None`分支。 调用`Path`、`_read`、`str`、`sidecar.stat`、`path.stat`、`bool`、`type`、`receipt.get`、`_label`等。 返回路径：L187的`result`。

</details>

**创建路径：** `workbench/capability_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L187。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6317`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "62745172e7955ed94ab554508a68deaa30cb636b12c4b4d7e2dee91beca44ea9"} -->
````python
# workbench/capability_diagnostics.py
"""Optional verifier failure facts; no product text, paths, or SDK messages."""

import json
from pathlib import Path

from workbench.settings import ROOT

STAGES = {
    "workbench/capability_sandbox.py": "verifier_controller",
    "workbench/capability_execution.py": "isolation_admission",
    "workbench/capability_dependencies.py": "dependency_admission",
    "workbench/capability_consumer.py": "consumer_contract",
    "workbench/capability_verification.py": "independent_oracle",
    "workbench/capability_browser_isolation.py": "browser_isolation",
    "workbench/sandbox.py": "sandbox_transport",
    "scripts/daytona_capability_profile.py": "container_inspection",
}
ERRORS = frozenset(
    {
        "CheckFailure",
        "BusinessCheckFailure",
        "CheckpointExpired",
        "BrowserFailure",
        "PrerequisiteError",
        "IsolationUnavailable",
        "ContainerInspectionRejected",
        "ValueError",
        "TypeError",
        "KeyError",
        "RuntimeError",
        "FileNotFoundError",
        "PermissionError",
        "TimeoutError",
        "TimeoutExpired",
        "ValidationError",
        "DaytonaError",
        "DaytonaNotFoundError",
    }
)
CLEANUP = frozenset(
    {
        "deleted",
        "not-started",
        "not-created",
        "pending",
        "delete-failed",
        "create-failed-unknown",
        "unconfirmed",
    }
)


def _read(path):
    try:
        with Path(path).open("rb") as source:
            raw = source.read(1_000_001)
        if len(raw) > 1_000_000:
            return {}
        result = json.loads(raw)
        return result if type(result) is dict else {}
    except OSError, ValueError, RecursionError:
        return {}


def _label(value, allowed):
    return value if type(value) is str and value in allowed else "other"


def record_failure(receipt_path, exc):
    """Write a separate diagnostic; never add fields to the acceptance receipt."""
    try:
        from workbench.filesystem import write_json

        failure = {"exception_type": _label(type(exc).__name__, ERRORS), "stage": "other"}
        trusted = {str(ROOT / name): stage for name, stage in STAGES.items()}
        frame = exc.__traceback__
        while frame is not None:
            stage = trusted.get(frame.tb_frame.f_code.co_filename)
            if stage is not None:
                failure.update(stage=stage, trusted_source_line=frame.tb_lineno)
            frame = frame.tb_next
        write_json(str(receipt_path) + ".diagnostic.json", failure)
    except Exception:
        pass  # Diagnostics cannot replace the verifier failure or interrupt cleanup.


def startup_diagnostic(value):
    """Re-filter existing startup facts; output hints never establish acceptance."""
    if type(value) is not dict:
        return None
    result = {}
    enums = {
        "phase": {"health_deadline"},
        "http_error": {"none", "connect", "timeout", "protocol", "other"},
        "command_exit_status": {"zero", "nonzero", "unknown"},
        "startup_phase_hint": {"unknown", "lifespan", "factory", "import"},
    }
    for key, allowed in enums.items():
        result[key] = _label(value.get(key), allowed)
    for key, lower, upper in (("http_status", 100, 599), ("command_exit_code", 0, 255)):
        number = value.get(key)
        result[key] = number if type(number) is int and lower <= number <= upper else None
    for key in (
        "application_startup_reported",
        "output_readable",
        "output_nonempty",
        "tmpfs_noexec",
    ):
        item = value.get(key)
        result[key] = item if type(item) is bool else None
    allowed_hints = (
        "permission-denied",
        "missing-module",
        "import-error",
        "native-library-mapping",
        "missing-file",
        "address-in-use",
        "readonly-filesystem",
        "storage-full",
        "memory-error",
        "syntax-error",
        "executable-format",
        "process-terminated",
    )
    hints = value.get("output_hints")
    result["output_hints"] = [
        name for name in allowed_hints if type(hints) is list and name in hints[:32]
    ]
    exception = value.get("exception_type")
    result["exception_type_hint"] = _label(
        exception,
        {
            "SyntaxError",
            "IndentationError",
            "ImportError",
            "ModuleNotFoundError",
            "NameError",
            "AttributeError",
            "TypeError",
            "ValueError",
            "KeyError",
            "RuntimeError",
            "PermissionError",
            "OSError",
            "FileNotFoundError",
            "MemoryError",
        },
    )
    target = value.get("target")
    if type(target) is dict:
        result["target_role"] = _label(target.get("role"), {"backend", "frontend"})
    return result


def node_diagnostic(product, *, aggregate):
    product = Path(product)
    path = product.parent / (
        product.name + ("-aggregate" if aggregate else "-node") + "-verification.json"
    )
    receipt = _read(path)
    sidecar = Path(str(path) + ".diagnostic.json")
    failure = _read(sidecar)
    try:
        if sidecar.stat().st_mtime_ns < path.stat().st_mtime_ns:
            failure = {}
    except OSError:
        failure = {}
    result = {
        "scope": "aggregate" if aggregate else "node",
        "receipt_available": bool(receipt),
        "passed": receipt.get("passed") if type(receipt.get("passed")) is bool else None,
        "cleanup": _label(receipt.get("cleanup"), CLEANUP),
        "exception_type": _label(failure.get("exception_type"), ERRORS),
        "stage": _label(failure.get("stage"), set(STAGES.values())),
    }
    line = failure.get("trusted_source_line")
    if type(line) is int and 0 < line < 1_000_000:
        result["trusted_source_line"] = line
    for key in ("checks", "obligation_checks", "browser"):
        value = receipt.get(key)
        result[key + "_count"] = len(value) if type(value) is list and len(value) <= 10000 else None
    for key in ("restarted", "backend_health_observed"):
        result[key] = receipt.get(key) if type(receipt.get(key)) is bool else None
    startup = startup_diagnostic(receipt.get("startup_diagnostic"))
    if startup is not None:
        result["startup"] = startup
    return result
````
