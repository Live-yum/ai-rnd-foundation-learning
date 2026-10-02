# tests/test_handbook_customer.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`、`scripts.handbook_notes`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_sourcebook_contains_every_customer_implementation_and_input`（L13–L48）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L33遍历`( "workbench/business*.py", "templates/business/**/*", "templates…`；L45断言`required <= names`；L46断言`"docs/business-platform.md" in GUIDES`；L47断言`not any(Path(name).name in {".env", "user.env"} for name in names)`；L48断言`list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md")) == [OUTPUT]`。 调用`sources`、`required.update`、`path.relative_to(ROOT).as_posix`、`path.relative_to`、`ROOT.glob`、`path.is_file`、`sorted`、`any`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_files_have_specific_architecture_and_component_notes`（L51–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52遍历`(ROOT / "workbench").glob("business*.py")`；L53断言`path.stem in MODULES`；L54遍历`(ROOT / "templates/business").rglob("*")`；L55按`not path.is_file() or "__pycache__" in path.parts`分支；L58断言`relative in BUSINESS_FILES`；L60断言`role == BUSINESS_FILES[relative]`；L61断言`all(role)`；L62断言`"Fa" in purpose("templates/business/fastapiadmin/index.vue")[0]`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / "workbench").glob`、`(ROOT / "templates/business").rglob`、`path.is_file`、`path.relative_to(ROOT / "templates/business").as_posix`、`path.relative_to`、`purpose`、`path.relative_to(ROOT).as_posix`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_learning_path_includes_real_initialization_and_all_three_templates`（L74–L95）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78遍历`(readme, guide, chapter)`；L79断言`"customer-service-decisions.md" in text`；L80断言`"customer-service-contract.md" in text`；L81断言`"bootstrap-admin --username manager" in text`；L82遍历`( "business_schema.build_metadata", "business_runtime.install_bus…`；L93断言`token in chapter`；L94断言`"原始需求逐项映射" in chapter`；L95断言`"亲手跑一遍完整客服操作" in chapter`。 调用`(ROOT / "README.md").read_text`、`(ROOT / "docs/guide.md").read_text`、`(ROOT / "docs/business-platform.md").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_model_lesson_has_exact_commit_gate_and_separate_template_evidence`（L98–L118）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L100遍历`( "feat/customer-service-acceptance", "native-probe.yml", "real_m…`；L116断言`token in text`；L117断言`"不预先声称任何模板已经通过" in text`；L118断言`"新库" in text and "重启" in text`。 调用`(ROOT / "docs/real-model-acceptance.md").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_screenshots_are_authentic_hashed_and_in_the_source_snapshot`（L121–L150）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L125断言`provenance["template"] == summary["workflow"]["template"] == "fastapiadmin"`；L126断言`provenance["genuine_model"] is True`；L127断言`summary["passed"] is True and summary["workflow"]["real_model"] is True`；L128断言`provenance["acceptance_scope"] == summary["acceptance_scope"] == "full_workflow"`；L129断言`provenance["source_sha"] == "a15137ff1aca04d3091a9c4f7cfa99bb09436d07"`；L130断言`summary["run_identity"] == [ str(provenance["run_id"]), str(provenance["run_attempt"]…`；L135断言`provenance["upstream_template_sha"] == "1cd12c726ad9032c17ef85ce805ce991be60fbdf"`；L137断言`len(provenance["screenshots"]) == 6`。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`(folder / "provenance.json").read_text`、`(folder / provenance["workflow_summary"]).read_text`、`str`、`sources`、`len`、`folder.glob`、`path.read_bytes`、`data.startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_images_follow_the_operation_they_explain`（L153–L183）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L167遍历`locations.items()`；L169断言`chapter.rfind("\n## ", 0, position) == chapter.index("\n" + heading)`；L171遍历`("操作位置", "预期", "FastapiAdmin", "a15137ff", "真实模型运行36789925373")`；L172断言`token in caption`；L173断言`f"](docs/images/customer-service/{image_name})" in rendered`；L175断言`len(images) == 6`；L176遍历`images`；L177断言`len(alt) >= 20`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / name).read_text`、`guide_text`、`locations.items`、`chapter.index`、`chapter.rfind`、`chapter[position:].split`、`re.findall`、`len`、`(ROOT / "docs" / relative).is_file`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook_customer.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L183。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8034`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook_customer.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bf2d9ec323cd6ae11c3860e3421eb458e0af871ebc0c8e1285ea2cc1b0aa88b3"} -->
````python
# tests/test_handbook_customer.py
"""The single from-zero sourcebook teaches and reconstructs the complete customer path."""

import hashlib
import json
import re
import struct
from pathlib import Path

from scripts.build_handbook import GUIDES, OUTPUT, ROOT, sources
from scripts.handbook_notes import BUSINESS_FILES, MODULES, PRODUCT, purpose


def test_sourcebook_contains_every_customer_implementation_and_input():
    names = {name for _, rows in sources() for name, _ in rows}
    required = {
        "docs/business-platform.md",
        "docs/real-model-acceptance.md",
        "examples/requirements/customer-service.md",
        "examples/requirements/customer-service-decisions.md",
        "examples/requirements/customer-service-contract.md",
        "examples/plans/customer-service.json",
        "scripts/business_fastapi_browser.cjs",
        "scripts/business_yudao_browser.cjs",
        "scripts/ci_real_model.py",
        ".github/workflows/customer-runtime.yml",
        ".github/workflows/native-probe.yml",
        ".github/workflows/real-model.yml",
        "tests/test_customer_workflow.py",
        "tests/test_business_capabilities.py",
        "tests/test_business_screenshots.py",
        "tests/test_handbook_customer.py",
    }
    for pattern in (
        "workbench/business*.py",
        "templates/business/**/*",
        "templates/product/business*.py",
        "templates/product/verify*business*",
        "templates/frontends/**/*",
    ):
        required.update(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.glob(pattern)
            if path.is_file() and "__pycache__" not in path.parts
        )
    assert required <= names, sorted(required - names)
    assert "docs/business-platform.md" in GUIDES
    assert not any(Path(name).name in {".env", "user.env"} for name in names)
    assert list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md")) == [OUTPUT]


def test_business_files_have_specific_architecture_and_component_notes():
    for path in (ROOT / "workbench").glob("business*.py"):
        assert path.stem in MODULES, path
    for path in (ROOT / "templates/business").rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT / "templates/business").as_posix()
        assert relative in BUSINESS_FILES, relative
        role = purpose(path.relative_to(ROOT).as_posix())
        assert role == BUSINESS_FILES[relative]
        assert all(role)
    assert "Fa" in purpose("templates/business/fastapiadmin/index.vue")[0]
    assert "Vben" in purpose("templates/business/yudao/panel.vue")[0]
    for name in (
        "business_schema.py",
        "business_runtime.py",
        "verify_business.py",
        "verify-business-browser.cjs",
    ):
        assert name in PRODUCT
        assert purpose("templates/product/" + name)[1] == PRODUCT[name]


def test_customer_learning_path_includes_real_initialization_and_all_three_templates():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs/guide.md").read_text(encoding="utf-8")
    chapter = (ROOT / "docs/business-platform.md").read_text(encoding="utf-8")
    for text in (readme, guide, chapter):
        assert "customer-service-decisions.md" in text
        assert "customer-service-contract.md" in text
        assert "bootstrap-admin --username manager" in text
    for token in (
        "business_schema.build_metadata",
        "business_runtime.install_business",
        "business_fastapi.extend_business",
        "business_yudao.install_yudao_business",
        "Fa/Element Plus",
        "Vben",
        "average_duration",
        "group_count",
        "time_count",
    ):
        assert token in chapter
    assert "原始需求逐项映射" in chapter
    assert "亲手跑一遍完整客服操作" in chapter


def test_real_model_lesson_has_exact_commit_gate_and_separate_template_evidence():
    text = (ROOT / "docs/real-model-acceptance.md").read_text(encoding="utf-8")
    for token in (
        "feat/customer-service-acceptance",
        "native-probe.yml",
        "real_model=true",
        "expected_sha",
        "GITHUB_SHA",
        "environment: rnd",
        "API_KEY: ${{ secrets.APK_KEY }}",
        "--template python-basic",
        "fastapiadmin",
        "yudao-vben",
        "reports/real-model/summary.json",
        "reports/real-model/screenshots/*.png",
        "smoke_only",
        "full_workflow",
    ):
        assert token in text
    assert "不预先声称任何模板已经通过" in text
    assert "新库" in text and "重启" in text


def test_customer_screenshots_are_authentic_hashed_and_in_the_source_snapshot():
    folder = ROOT / "docs/images/customer-service"
    provenance = json.loads((folder / "provenance.json").read_text(encoding="utf-8"))
    summary = json.loads((folder / provenance["workflow_summary"]).read_text(encoding="utf-8"))
    assert provenance["template"] == summary["workflow"]["template"] == "fastapiadmin"
    assert provenance["genuine_model"] is True
    assert summary["passed"] is True and summary["workflow"]["real_model"] is True
    assert provenance["acceptance_scope"] == summary["acceptance_scope"] == "full_workflow"
    assert provenance["source_sha"] == "a15137ff1aca04d3091a9c4f7cfa99bb09436d07"
    assert summary["run_identity"] == [
        str(provenance["run_id"]),
        str(provenance["run_attempt"]),
        provenance["source_sha"],
    ]
    assert provenance["upstream_template_sha"] == "1cd12c726ad9032c17ef85ce805ce991be60fbdf"
    source_rows = {name: content for _, rows in sources() for name, content in rows}
    assert len(provenance["screenshots"]) == 6
    assert {row["file"] for row in provenance["screenshots"]} == {
        path.name for path in folder.glob("*.png")
    }
    for entry in provenance["screenshots"]:
        path = folder / entry["file"]
        data = path.read_bytes()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert struct.unpack(">II", data[16:24]) == (entry["width"], entry["height"])
        assert entry["pixel_reviewed"] is True and entry["modified"] is False
        assert source_rows[path.relative_to(ROOT).as_posix()] == data
    assert "docs/images/customer-service/provenance.json" in source_rows
    assert "docs/images/customer-service/genuine-workflow-summary.json" in source_rows


def test_customer_images_follow_the_operation_they_explain():
    from scripts.build_handbook import guide_text

    name = "docs/business-platform.md"
    chapter = (ROOT / name).read_text(encoding="utf-8")
    locations = {
        "manager-customers-native-form.png": "## 1.",
        "employee-native-list.png": "## 2.",
        "manager-requests-assignment.png": "## 3.",
        "service-handling-history.png": "## 5.",
        "employee-resolution-reminders.png": "## 5.",
        "manager-native-dashboard.png": "## 5.",
    }
    rendered = guide_text(name)
    for image_name, heading in locations.items():
        position = chapter.index(f"](images/customer-service/{image_name})")
        assert chapter.rfind("\n## ", 0, position) == chapter.index("\n" + heading)
        caption = chapter[position:].split("\n\n", 2)[1]
        for token in ("操作位置", "预期", "FastapiAdmin", "a15137ff", "真实模型运行36789925373"):
            assert token in caption
        assert f"](docs/images/customer-service/{image_name})" in rendered
    images = re.findall(r"!\[([^\]]+)\]\((images/[^)]+)\)", chapter)
    assert len(images) == 6
    for alt, relative in images:
        assert len(alt) >= 20
        assert (ROOT / "docs" / relative).is_file()
    assert "PNG原始字节" in (ROOT / "docs/guide.md").read_text(encoding="utf-8")
    assert "不代表后续提交" in chapter
    assert "不是模拟接口或绘制的UI" in chapter
    assert "本章没有为这些页面补画截图" in chapter
    assert "data:image" not in chapter
````
