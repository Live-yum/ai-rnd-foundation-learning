"""Real native Plop + Aider repair + backend/frontend/browser/fresh DB acceptance."""

import argparse
import json
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from scripts.native_coding_fixture import NativeCodingFixture
from workbench.domain import CustomRule
from workbench.filesystem import write_json
from workbench.native import prepare_sources
from workbench.native_coding import native_rule_customizer
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--output", type=Path, default=ROOT / ".native/tool-product")
    args = parser.parse_args()
    settings = Settings(
        data_dir=ROOT / ".data/native-tools",
        coding_engine="aider",
        tool_timeout=900,
        _env_file=None,
    )
    sources = {row["slot"]: Path(row["path"]) for row in prepare_sources(settings, args.template)}
    plan = acceptance_spec()
    plan.custom_rules = [
        CustomRule(
            description="quantity不能为负；新增和修改都校验，前端也要提示。",
            entity="device",
            accept_examples=[
                {"name": "device-rule", "quantity": 0, "active": False},
                {"name": "device-rule-second", "quantity": 7, "active": True},
            ],
            reject_examples=[{"name": "device-rule", "quantity": -1, "active": False}],
        )
    ]
    fixture = NativeCodingFixture(fail_first=True)
    reports = ROOT / "reports/native-tools"
    outcome = {
        "passed": False,
        "template": args.template,
        "model_transport": "explicit-fixture",
        "model_calls": 0,
    }
    try:
        actual_customization = native_rule_customizer(settings, fixture, "ci-native")

        def interrupted(*args):
            raise RuntimeError("explicit-test-interruption-after-native-generation")

        try:
            run_acceptance(
                args.template,
                sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
                args.output if args.template == "fastapiadmin" else args.output / "backend",
                sources.get("frontend"),
                os.environ["NATIVE_TEST_DATABASE_URL"],
                reports,
                plan,
                customization=interrupted,
            )
        except RuntimeError as exc:
            if str(exc) != "explicit-test-interruption-after-native-generation":
                raise
        else:
            raise AssertionError("Native interruption fixture did not run")
        checkpoint = json.loads((reports / "recovery.json").read_text(encoding="utf-8"))
        assert checkpoint["resumable"] and checkpoint["targets"]
        import workbench.native_lab as native_lab

        real_permissions = native_lab.generated_permissions
        permission_attempts = []

        def interrupt_after_permissions(*values):
            result = real_permissions(*values)
            permission_attempts.append(result["attempt_id"])
            raise RuntimeError("explicit-test-interruption-after-native-permissions")

        native_lab.generated_permissions = interrupt_after_permissions
        try:
            run_acceptance(
                args.template,
                sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
                args.output if args.template == "fastapiadmin" else args.output / "backend",
                sources.get("frontend"),
                os.environ["NATIVE_TEST_DATABASE_URL"],
                reports,
                plan,
                customization=actual_customization,
            )
        except RuntimeError as exc:
            if str(exc) != "explicit-test-interruption-after-native-permissions":
                raise
        else:
            raise AssertionError("Native permission interruption fixture did not run")
        finally:
            native_lab.generated_permissions = real_permissions
        report = run_acceptance(
            args.template,
            sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
            args.output if args.template == "fastapiadmin" else args.output / "backend",
            sources.get("frontend"),
            os.environ["NATIVE_TEST_DATABASE_URL"],
            reports,
            plan,
            customization=actual_customization,
        )
        final_permissions = json.loads(
            (reports / "generated/permissions.json").read_text(encoding="utf-8")
        )
        assert final_permissions["attempt_id"] not in permission_attempts
        edits = json.loads((reports / "native-coding.json").read_text())
        first = json.loads((reports / "coding-0.json").read_text())
        assert edits["passed"] and edits["repaired"] and edits["attempts"] == 2
        assert first["rolled_back"] and not first["verified"]
        assert report["portable_restored"]["business_rules"]["passed"]
        outcome.update(
            passed=True,
            actual_aider=True,
            actual_plop=True,
            actual_browser=True,
            automatic_repair=True,
            rollback_verified=True,
            same_run_resume=True,
            source_database_preserved=True,
            fresh_database=True,
            native_report=report,
        )
    finally:
        write_json(reports / "toolchain-acceptance.json", outcome)
    print(
        json.dumps(
            {
                "passed": True,
                "template": args.template,
                "actual_aider": True,
                "actual_plop": True,
                "repair": True,
            }
        )
    )


if __name__ == "__main__":
    main()
