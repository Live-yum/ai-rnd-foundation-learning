# tools/mini-swe/worker.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `rpc`（L19–L27）：接收`operation`、`payload`。 控制顺序：L22按`not line or len(line) > LIMIT`分支；L23抛异常，停止当前正常路径；L25按`"error" in result`分支；L26抛异常，停止当前正常路径。 调用`print`、`json.dumps`、`sys.stdin.buffer.readline`、`len`、`ValueError`、`json.loads`。 返回路径：L27的`result["result"]`。
- `PlatformModel`（L30–L57）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `PlatformModel.query`（L31–L37）：接收`messages`。 调用`rpc`。 返回路径：L33的`{ "role": "assistant", "content": "structured business-file action", "extra": {"actions": …`。
- `PlatformModel.format_message`（L39–L40）：接收`**kwargs`。 返回路径：L40的`kwargs`。
- `PlatformModel.format_observation_messages`（L42–L51）：接收`message`、`outputs`、`template_vars`。 控制顺序：L43按`outputs and outputs[-1].get("submitted")`分支。 调用`outputs[-1].get`、`json.dumps`。 返回路径：L44的`[ { "role": "exit", "content": "candidate submitted", "extra": {"exit_status": "Submitted"…`；L51的`[{"role": "user", "content": json.dumps(outputs)}]`。
- `PlatformModel.get_template_vars`（L53–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L54的`{}`。
- `PlatformModel.serialize`（L56–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L57的`{"model": "platform-gateway", "billing_authority": "platform-reservations"}`。
- `DaytonaEnvironment`（L60–L70）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DaytonaEnvironment.execute`（L61–L64）：接收`action`。 控制顺序：L62按`action.get("operation") not in {"edit", "submit", "edit_and_submit"}`分支；L63抛异常，停止当前正常路径。 调用`action.get`、`ValueError`、`rpc`。 返回路径：L64的`rpc("environment", action)`。
- `DaytonaEnvironment.get_template_vars`（L66–L67）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L67的`{"environment": "approved-local-daytona"}`。
- `DaytonaEnvironment.serialize`（L69–L70）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L70的`{"environment": "platform-daytona-rpc", "local_execution": False}`。
- `main`（L73–L98）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L75按`set(initial) != {"task", "max_steps", "timeout"}`分支；L76抛异常，停止当前正常路径。 调用`json.loads`、`sys.stdin.buffer.readline`、`set`、`ValueError`、`DefaultAgent`、`PlatformModel`、`DaytonaEnvironment`、`agent.run`、`print`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tools/mini-swe/worker.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L102。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3325`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/mini-swe/worker.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "00b14abce0d5aba1b64f6e0c5390ced54570f435e29c0aac6b6e03be38dc730f"} -->
````python
# tools/mini-swe/worker.py
"""Python 3.12 mini-SWE driver. No credentials, shell environment, or product mount.

JSON-line RPC delegates model access and filesystem edits to the platform. The
custom Environment intentionally has no execute-command operation.
"""

import json
import sys
from importlib.metadata import version

if sys.version_info[:2] != (3, 12) or version("mini-swe-agent") != "2.4.6":
    raise RuntimeError("Worker requires reviewed Python 3.12 and mini-swe-agent 2.4.6")

from minisweagent.agents.default import DefaultAgent

LIMIT = 1_200_000


def rpc(operation, payload):
    print(json.dumps({"operation": operation, "payload": payload}), flush=True)
    line = sys.stdin.buffer.readline(LIMIT + 1)
    if not line or len(line) > LIMIT:
        raise ValueError("bounded RPC response missing")
    result = json.loads(line)
    if "error" in result:
        raise ValueError("platform rejected worker operation")
    return result["result"]


class PlatformModel:
    def query(self, messages):
        turn = rpc("model", {"messages": messages})
        return {
            "role": "assistant",
            "content": "structured business-file action",
            "extra": {"actions": [turn], "cost": 0.0},
        }

    def format_message(self, **kwargs):
        return kwargs

    def format_observation_messages(self, message, outputs, template_vars):
        if outputs and outputs[-1].get("submitted"):
            return [
                {
                    "role": "exit",
                    "content": "candidate submitted",
                    "extra": {"exit_status": "Submitted", "submission": "candidate"},
                }
            ]
        return [{"role": "user", "content": json.dumps(outputs)}]

    def get_template_vars(self):
        return {}

    def serialize(self):
        return {"model": "platform-gateway", "billing_authority": "platform-reservations"}


class DaytonaEnvironment:
    def execute(self, action):
        if action.get("operation") not in {"edit", "submit", "edit_and_submit"}:
            raise ValueError("No shell commands or local execution are supported")
        return rpc("environment", action)

    def get_template_vars(self):
        return {"environment": "approved-local-daytona"}

    def serialize(self):
        return {"environment": "platform-daytona-rpc", "local_execution": False}


def main():
    initial = json.loads(sys.stdin.buffer.readline(LIMIT + 1))
    if set(initial) != {"task", "max_steps", "timeout"}:
        raise ValueError("unexpected worker configuration")
    agent = DefaultAgent(
        PlatformModel(),
        DaytonaEnvironment(),
        system_template=(
            "Only edit approved business files. Use edit_and_submit when ready for checking; "
            "edit alone continues editing, submit checks existing edits. No shell actions."
        ),
        instance_template="{{ task }}",
        step_limit=initial["max_steps"],
        wall_time_limit_seconds=initial["timeout"],
        cost_limit=0,
    )
    result = agent.run(initial["task"])
    print(
        json.dumps(
            {
                "operation": "result",
                "payload": {"exit_status": result.get("exit_status"), "steps": agent.n_calls},
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
````
