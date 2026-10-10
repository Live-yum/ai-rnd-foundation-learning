"""Explicit new-run compilation; persisted V1 gates are never migrated in place."""

from workbench.planning.contracts import CapabilityTaskV2
from workbench.planning.feature_planner import FeatureDesign, PlannedModuleV2


def compile_v2(design, *, executor="bounded_edit", max_steps=8):
    if design.outline.version == 2:
        for module in design.outline.modules:
            expected = executor if module.extension == "approved-source-module" else "bounded_edit"
            if module.executor != expected or module.max_steps != (
                max_steps if expected == "mini_swe" else 1
            ):
                raise ValueError(
                    "planner cannot expand the run's configured executor or step budget"
                )
        return FeatureDesign.model_validate(design.model_dump())
    data = design.model_dump()
    data["outline"]["version"] = 2
    for module in data["outline"]["modules"]:
        engine = executor if module["extension"] == "approved-source-module" else "bounded_edit"
        module.update(
            version=2,
            task_id=module["id"],
            executor=engine,
            requirement_ids=module["requirements"],
            allowed_paths=module["files"],
            acceptance_ids=module["scenarios"],
            max_steps=max_steps if engine == "mini_swe" else 1,
        )
        PlannedModuleV2.model_validate(module)
    if data["implementation"]:
        data["implementation"]["version"] = 2
        modules = {module["id"]: module for module in data["outline"]["modules"]}
        tasks = []
        for old in data["implementation"]["tasks"]:
            # Validate V1 equivalence BEFORE projecting a module into an execution task.
            module = modules.get(old["id"])
            if module is None or any(module[key] != value for key, value in old.items()):
                raise ValueError("planner module and execution task disagree")
            tasks.append({key: module[key] for key in CapabilityTaskV2.model_fields})
        data["implementation"]["tasks"] = tasks
    return FeatureDesign.model_validate(data)


def version_for_run(run):
    return run.get("options", {}).get("production_version", 1)
