# workbench/coding/timing.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `http_trace_receipt`（L39–L49）：接收`value`。 源码说明：Fixed phases and bounded numbers only; never retain trace info or exceptions.。 控制顺序：L41按`not isinstance(value, dict)`分支。 调用`isinstance`、`value.get`、`type`、`numeric`、`HTTP_TRACE_TIMES.items`。 返回路径：L42的`None`；L45的`{ "event_count": count if type(count) is int and 0 <= count <= 64 else None, "failed_phase…`。
- `numeric`（L52–L57）：接收`value`、`maximum`。 调用`type`、`math.isfinite`、`round`。 返回路径：L53的`round(value, 4) if type(value) in (int, float) and 0 <= value <= maximum and math.isfinite…`。
- `timing_receipts`（L60–L84）：接收`values`、`attempts`。 控制顺序：L62按`not isinstance(values, list)`分支。 调用`isinstance`、`numeric`、`value.get`、`fields.items`、`http_trace_receipt`、`type`。 返回路径：L63的`[]`；L64的`[ { **{key: numeric(value.get(key), limit) for key, limit in fields.items()}, **( {"http_t…`。
- `read_turns`（L87–L93）：接收`path`。 控制顺序：L89按`path.stat().st_size > 32768`分支。 调用`path.stat`、`timing_receipts`、`json.loads`、`path.read_text`。 返回路径：L90的`[]`；L91的`timing_receipts(json.loads(path.read_text()))`；L93的`[]`。
- `record_turn`（L97–L120）：接收`path`、`step`、`deadline`、`timeout`、`payload`、`transport`。 调用`time.monotonic`、`max`、`len`、`json.dumps`、`getattr`、`value.update`、`write_json`、`timing_receipts`、`read_turns`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/coding/timing.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L120。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3849`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/coding/timing.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f82eb2598da974bbea3f8c9329dc701d373eb82229a175cfa2c86943c16016f8"} -->
````python
# workbench/coding/timing.py
"""Optional fixed-label/numeric diagnostics; never execution authority."""

import json
import math
import time
from contextlib import contextmanager

from workbench.filesystem import write_json

TURN_FIELDS = {
    "step": 8,
    "module_remaining_seconds": 180,
    "work_remaining_seconds": 180,
    "timeout_seconds": 180,
    "elapsed_seconds": 5400,
    "remaining_after_seconds": 180,
    "overrun_seconds": 5400,
    "payload_chars": 40000,
    "http_attempts_before": 32,
    "http_attempts_after": 32,
}
ATTEMPT_FIELDS = {
    "attempt": 32,
    "request_body_bytes": 1_000_000,
    "read_timeout_seconds": 180,
    "headers_seconds": 5400,
    "elapsed_seconds": 5400,
    "response_bytes": 2_000_000,
}
HTTP_TRACE_PHASES = ("connect", "tls", "request_headers", "request_body", "response_headers")
HTTP_TRACE_TIMES = {
    f"{phase}_{state}_seconds": 5400
    for phase in HTTP_TRACE_PHASES
    for state in ("started", "complete", "failed")
}
TURN_OPERATIONS = ("edit", "submit", "edit_and_submit")


def http_trace_receipt(value):
    """Fixed phases and bounded numbers only; never retain trace info or exceptions."""
    if not isinstance(value, dict):
        return None
    phase = value.get("failed_phase")
    count = value.get("event_count")
    return {
        "event_count": count if type(count) is int and 0 <= count <= 64 else None,
        "failed_phase": phase if type(phase) is str and phase in HTTP_TRACE_PHASES else None,
        **{key: numeric(value.get(key), limit) for key, limit in HTTP_TRACE_TIMES.items()},
    }


def numeric(value, maximum):
    return (
        round(value, 4)
        if type(value) in (int, float) and 0 <= value <= maximum and math.isfinite(value)
        else None
    )


def timing_receipts(values, *, attempts=False):
    fields = ATTEMPT_FIELDS if attempts else TURN_FIELDS
    if not isinstance(values, list):
        return []
    return [
        {
            **{key: numeric(value.get(key), limit) for key, limit in fields.items()},
            **(
                {"http_trace": http_trace_receipt(value["http_trace"])}
                if attempts and "http_trace" in value
                else {}
            ),
            **(
                {
                    "operation": value["operation"]
                    if type(value["operation"]) is str and value["operation"] in TURN_OPERATIONS
                    else None
                }
                if not attempts and "operation" in value
                else {}
            ),
        }
        for value in values[: 32 if attempts else 8]
        if isinstance(value, dict)
    ]


def read_turns(path):
    try:
        if path.stat().st_size > 32768:
            return []
        return timing_receipts(json.loads(path.read_text()))
    except OSError, ValueError, TypeError:
        return []


@contextmanager
def record_turn(path, step, deadline, timeout, payload, transport):
    started = time.monotonic()
    value = {
        "step": step,
        "module_remaining_seconds": max(0, deadline - started),
        "work_remaining_seconds": max(0, deadline - started - 15),
        "timeout_seconds": timeout,
        "payload_chars": len(json.dumps(payload, ensure_ascii=False)),
        "http_attempts_before": getattr(transport, "calls", None),
    }
    try:
        yield value
    finally:
        ended = time.monotonic()
        value.update(
            elapsed_seconds=max(0, ended - started),
            remaining_after_seconds=max(0, deadline - ended),
            overrun_seconds=max(0, ended - deadline),
            http_attempts_after=getattr(transport, "calls", None),
        )
        try:
            write_json(path, timing_receipts([*read_turns(path), value]))
        except OSError, ValueError, TypeError:
            pass  # Optional diagnostics cannot replace the model outcome.
````
