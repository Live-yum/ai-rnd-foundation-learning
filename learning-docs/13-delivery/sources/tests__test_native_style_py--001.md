# tests/test_native_style.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.native_recovery`、`workbench.native_style`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `sample`（L12–L43）：接收`tmp_path`、`template`。 控制顺序：L14遍历`PROFILES[template]["protected"]`；L18按`template == "fastapiadmin"`分支。 调用`prefix.endswith`、`atomic_text`、`SimpleNamespace`。 返回路径：L43的`source, generated, SimpleNamespace(entities=[SimpleNamespace(name="device")]), page`。
- `test_native_style_retains_exact_shell_and_parsed_native_components`（L47–L52）：接收`tmp_path`、`template`。 控制顺序：L50断言`report["passed"] is True and report["shell_and_theme_unchanged"] is True`；L51断言`report["generic_frontend_substitution"] is False`；L52断言`report["generated_pages"] and report["protected_files"]`。 调用`sample`、`verify_native_style`、`pytest.mark.parametrize`、`list`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_style_rejects_substitutions`（L59–L76）：接收`tmp_path`、`template`、`change`。 控制顺序：L62按`change == "shell"`分支；L64按`change == "theme_missing"`分支；L66按`change == "new_override"`分支。 调用`sample`、`atomic_text`、`(generated / (prefixes[0] + "shell.vue")).unlink`、`(generated / page).read_text`、`pytest.raises`、`verify_native_style`、`pytest.mark.parametrize`、`list`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_style_requires_actual_native_workflow_widgets`（L80–L113）：接收`tmp_path`、`template`。 控制顺序：L87按`template == "fastapiadmin"`分支；L97遍历`("panel.vue", "metric-chart.vue")`；L104断言`report["passed"] is True`。 调用`sample`、`shutil.copyfile`、`native_page.write_text`、`native_page.read_text(encoding="utf-8").replace`、`native_page.read_text`、`atomic_text`、`(ROOT / "templates/business/yudao" / name).read_text`、`verify_native_style`、`broken.write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_style.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L113。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4848`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_style.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d527335d0dfdb63ac4e5dbbc920c5a1b73dabf751278a945add27b2090bc77a9"} -->
````python
# tests/test_native_style.py
"""Fail-closed native shell/component contracts, not screenshot substitutes."""

from types import SimpleNamespace

import pytest

from workbench.filesystem import atomic_text
from workbench.native_recovery import NativeIntegrityError
from workbench.native_style import PROFILES, verify_native_style


def sample(tmp_path, template):
    source, generated = tmp_path / "upstream", tmp_path / "generated"
    for prefix in PROFILES[template]["protected"]:
        path = prefix + "shell.vue" if prefix.endswith("/") else prefix
        atomic_text(source / path, "upstream-identity")
        atomic_text(generated / path, "upstream-identity")
    if template == "fastapiadmin":
        page = "src/views/module_rnd/device/index.vue"
        atomic_text(
            generated / page,
            "<template><FaSearchBar/><FaTable/><FaDialog><FaForm/></FaDialog></template>",
        )
    else:
        root = "apps/web-antd/src/views/infra/wbdevice"
        page = root + "/index.vue"
        atomic_text(
            generated / page,
            """<script setup lang="ts">
import { Page } from '@vben/common-ui';
import { useVbenVxeGrid, TableAction } from '#/adapter/vxe-table';
import { message } from 'ant-design-vue';
</script><template><Page><Grid><TableAction/></Grid></Page></template>""",
        )
        atomic_text(
            generated / (root + "/modules/form.vue"),
            """<script setup lang="ts">
import { useVbenModal } from '@vben/common-ui';
import { useVbenForm } from '#/adapter/form';
import { message } from 'ant-design-vue';
</script><template><Modal><Form/></Modal></template>""",
        )
    return source, generated, SimpleNamespace(entities=[SimpleNamespace(name="device")]), page


@pytest.mark.parametrize("template", list(PROFILES))
def test_native_style_retains_exact_shell_and_parsed_native_components(tmp_path, template):
    source, generated, plan, _ = sample(tmp_path, template)
    report = verify_native_style(template, source, generated, plan, tmp_path / "reports")
    assert report["passed"] is True and report["shell_and_theme_unchanged"] is True
    assert report["generic_frontend_substitution"] is False
    assert report["generated_pages"] and report["protected_files"]


@pytest.mark.parametrize("template", list(PROFILES))
@pytest.mark.parametrize(
    "change", ["shell", "theme_missing", "new_override", "generic", "comment_only"]
)
def test_native_style_rejects_substitutions(tmp_path, template, change):
    source, generated, plan, page = sample(tmp_path, template)
    prefixes = PROFILES[template]["protected"]
    if change == "shell":
        atomic_text(generated / (prefixes[0] + "shell.vue"), "different shell")
    elif change == "theme_missing":
        (generated / (prefixes[0] + "shell.vue")).unlink()
    elif change == "new_override":
        atomic_text(generated / (prefixes[0] + "override.css"), "body { background: red }")
    else:
        old = (generated / page).read_text(encoding="utf-8")
        atomic_text(
            generated / page,
            ("<!--" + old + "-->" if change == "comment_only" else "")
            + '<template><div id="workspace"><table/></div></template>',
        )
    with pytest.raises(NativeIntegrityError):
        verify_native_style(template, source, generated, plan, tmp_path / "reports")


@pytest.mark.parametrize("template", list(PROFILES))
def test_business_style_requires_actual_native_workflow_widgets(tmp_path, template):
    import shutil

    from workbench.settings import ROOT

    source, generated, plan, page = sample(tmp_path, template)
    plan.business = True
    if template == "fastapiadmin":
        shutil.copyfile(ROOT / "templates/business/fastapiadmin/index.vue", generated / page)
        victim, component = page, "ElTimeline"
    else:
        native_page = generated / page
        native_page.write_text(
            native_page.read_text(encoding="utf-8").replace("<Page>", "<Page><RndBusinessPanel/>"),
            encoding="utf-8",
        )
        root = "apps/web-antd/src/views/infra/rnd-business/"
        for name in ("panel.vue", "metric-chart.vue"):
            atomic_text(
                generated / (root + name),
                (ROOT / "templates/business/yudao" / name).read_text(encoding="utf-8"),
            )
        victim, component = root + "metric-chart.vue", "EchartsUI"
    report = verify_native_style(template, source, generated, plan, tmp_path / "reports")
    assert report["passed"] is True
    broken = generated / victim
    broken.write_text(
        broken.read_text(encoding="utf-8")
        .replace("<" + component, "<GenericWidget")
        .replace("</" + component, "</GenericWidget"),
        encoding="utf-8",
    )
    with pytest.raises(NativeIntegrityError):
        verify_native_style(template, source, generated, plan, tmp_path / "reports")
````
