"""OpenSpec produces documents; Feature Planner still owns executable contracts."""

from workbench.core.contracts import digest
from workbench.filesystem import inside, write_json
from workbench.specifications.artifact_writer import initialize_workspace, write_artifacts
from workbench.specifications.openspec.cli import ARTIFACTS, OpenSpecCLI
from workbench.specifications.validator import (
    SpecificationBundle,
    validate_mapping,
    validate_sources,
)


def prepare_specifications(settings, gateway, run_id, scope, selection, round_number):
    workspace = inside(
        settings.data_dir, f"runs/{run_id}/specifications/{scope['source_digest']}/{round_number}"
    )
    initialize_workspace(workspace)
    cli = OpenSpecCLI(workspace)
    cli.check_version()
    cli.validate_schema()
    if not inside(workspace, "openspec/changes/product/.openspec.yaml").exists():
        cli.new_change()
    # Instructions are data, and cannot select apply/archive or a coding workflow.
    instructions = {name: cli.instructions(name) for name in ARTIFACTS}
    bundle = gateway.complete(
        run_id,
        f"plan:specifications:{scope['source_digest']}:{round_number}",
        "生成 proposal/specs/design/tasks 文档。完整保留来源、验收与阻塞；文档不授权执行。",
        {"scope": scope, "selection": selection, "instructions": instructions},
        SpecificationBundle,
    )
    validate_sources(bundle, scope)
    write_artifacts(workspace, bundle)
    status = cli.status()
    if status.get("schemaName") != "rnd-factory" or status.get("isComplete") is not True:
        raise ValueError("OpenSpec document artifacts are incomplete")
    return bundle, workspace


def bind_feature_design(workspace, bundle, design, scope, selection):
    mapping = validate_mapping(bundle, design, scope, selection)
    write_json(
        inside(workspace, "feature-mapping.json"),
        {
            **mapping,
            "documents_digest": digest(bundle.model_dump()),
            "feature_design_digest": digest(design.model_dump()),
        },
    )
