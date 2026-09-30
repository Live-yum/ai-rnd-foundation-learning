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
            native_page.read_text().replace("<Page>", "<Page><RndBusinessPanel/>")
        )
        root = "apps/web-antd/src/views/infra/rnd-business/"
        for name in ("panel.vue", "metric-chart.vue"):
            atomic_text(
                generated / (root + name), (ROOT / "templates/business/yudao" / name).read_text()
            )
        victim, component = root + "metric-chart.vue", "EchartsUI"
    report = verify_native_style(template, source, generated, plan, tmp_path / "reports")
    assert report["passed"] is True
    broken = generated / victim
    broken.write_text(
        broken.read_text()
        .replace("<" + component, "<GenericWidget")
        .replace("</" + component, "</GenericWidget")
    )
    with pytest.raises(NativeIntegrityError):
        verify_native_style(template, source, generated, plan, tmp_path / "reports")
