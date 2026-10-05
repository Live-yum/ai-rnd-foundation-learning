# tests/test_capability_browser_apparmor.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_explicit_default_required_in_both_lifecycle_states`（L16–L28）：接收`monkeypatch`、`state`。 控制顺序：L20断言`"--security-opt=apparmor=docker-default" in command`；L21断言`"--env=CAPABILITY_BROWSER_REQUIRE_APPARMOR=1" in command`；L25遍历`("", None, "unconfined", "different")`。 调用`approved`、`monkeypatch.setattr`、`isolation.worker_command`、`worker_inspection`、`isolation.require_worker_inspection`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_apparmor_option_and_runtime_guard_cannot_be_dropped`（L31–L40）：接收`monkeypatch`。 调用`approved`、`worker_inspection`、`value[0]["HostConfig"]["SecurityOpt"].remove`、`pytest.raises`、`isolation.require_worker_inspection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_kernel_label_must_be_exact_enforce`（L59–L85）：接收`label`。 控制顺序：L61按`not node`分支；L81断言`result.returncode == 0`；L82断言`json.loads(result.stdout) == { "passed": label in {"docker-default (enforce)", "docke…`。 调用`shutil.which`、`pytest.skip`、`Path(__file__).resolve`、`Path`、`subprocess.run`、`str`、`json.dumps`、`json.loads`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_raw_probe_checks_label_before_any_syscall_case`（L88–L96）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L93断言`main.index("if (!apparmor_enforced())") < main.index('socket_case("native_inet_socket…`；L94断言`policy.POLICY_SHA256 == "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4…`。 调用`( Path(__file__).resolve().parents[1] / "scripts/capability_brows…`、`Path(__file__).resolve`、`Path`、`source.index`、`main.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_guard_environment_is_unique`（L109–L114）：接收`monkeypatch`、`env`。 调用`approved`、`worker_inspection`、`pytest.raises`、`isolation.require_worker_inspection`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_apparmor.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L114。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4397`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_apparmor.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "effaf7e20d0f6c5280565dcf109890dc95a6531865338950693acde69874cd0b"} -->
````python
# tests/test_capability_browser_apparmor.py
"""Same-default AppArmor binding regressions; no live security policy changes."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.test_capability_browser_policy import IMAGE, NAME, approved, worker_inspection
from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy


@pytest.mark.parametrize("state", ["created", "running"])
def test_explicit_default_required_in_both_lifecycle_states(monkeypatch, state):
    approved(monkeypatch)
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: {})
    command = isolation.worker_command(IMAGE, NAME)
    assert "--security-opt=apparmor=docker-default" in command
    assert "--env=CAPABILITY_BROWSER_REQUIRE_APPARMOR=1" in command
    value = worker_inspection()
    value[0]["State"] = {"Status": state, "Running": state == "running"}
    isolation.require_worker_inspection(value, IMAGE)
    for label in ("", None, "unconfined", "different"):
        value[0]["AppArmorProfile"] = label
        with pytest.raises(ValueError, match="apparmor-config"):
            isolation.require_worker_inspection(value, IMAGE)


def test_apparmor_option_and_runtime_guard_cannot_be_dropped(monkeypatch):
    approved(monkeypatch)
    value = worker_inspection()
    value[0]["HostConfig"]["SecurityOpt"].remove("apparmor=docker-default")
    with pytest.raises(ValueError, match="security-options"):
        isolation.require_worker_inspection(value, IMAGE)
    value = worker_inspection()
    value[0]["Config"]["Env"] = []
    with pytest.raises(ValueError, match="apparmor-runtime-guard"):
        isolation.require_worker_inspection(value, IMAGE)


@pytest.mark.parametrize(
    "label",
    [
        "docker-default (enforce)",
        "docker-default (enforce)\n",
        "",
        "unconfined\n",
        "docker-default (complain)\n",
        "other (enforce)\n",
        " docker-default (enforce)\n",
        "docker-default (enforce)\nextra",
        "docker-default (enforce)\x00extra",
        "\u00e4ocker-default (enforce)",
        None,
    ],
)
def test_actual_kernel_label_must_be_exact_enforce(label):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node tooling unavailable; mandatory on Actions")
    script = Path(__file__).resolve().parents[1] / "scripts/capability_browser_apparmor.cjs"
    harness = """
const {requireAppArmor} = require(process.argv[1])
const input = JSON.parse(process.argv[2]);let closed=0
const api = {
 openSync: (path, mode) => {if(path!='/proc/self/attr/current'||mode!='r')throw Error('path');if(input===null)throw Error('unreadable');return 3},
 readSync: (_fd,b,_o,size,_p) => {if(size!==128)throw Error('bound');return b.write(input)},
 closeSync:()=>closed++,
}
let passed=false;try{passed=requireAppArmor(api)}catch{}
process.stdout.write(JSON.stringify({passed,closed}))
"""
    result = subprocess.run(
        [node, "-e", harness, str(script), json.dumps(label)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "passed": label in {"docker-default (enforce)", "docker-default (enforce)\n"},
        "closed": 0 if label is None else 1,
    }


def test_raw_probe_checks_label_before_any_syscall_case():
    source = (
        Path(__file__).resolve().parents[1] / "scripts/capability_browser_seccomp_probe.c"
    ).read_text()
    main = source[source.index("int main(void)") :]
    assert main.index("if (!apparmor_enforced())") < main.index('socket_case("native_inet_socket"')
    assert (
        policy.POLICY_SHA256 == "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"
    )


@pytest.mark.parametrize(
    "env",
    [
        None,
        "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1",
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=0"],
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1"],
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", None],
    ],
)
def test_runtime_guard_environment_is_unique(monkeypatch, env):
    approved(monkeypatch)
    value = worker_inspection()
    value[0]["Config"]["Env"] = env
    with pytest.raises(ValueError, match="apparmor-runtime-guard"):
        isolation.require_worker_inspection(value, IMAGE)
````
