"""The single from-zero sourcebook teaches and reconstructs the complete customer path."""

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
