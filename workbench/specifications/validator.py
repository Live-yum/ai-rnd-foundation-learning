"""Strict source-bound document contracts; Markdown cannot authorize execution."""

from pydantic import Field, model_validator

from workbench.core.contracts import Contract
from workbench.planning.contracts import Identifier


class SpecificationBundle(Contract):
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    requirement_ids: list[Identifier] = Field(min_length=1, max_length=256)
    proposal: str = Field(min_length=1, max_length=20000)
    specs: str = Field(min_length=1, max_length=40000)
    design: str = Field(min_length=1, max_length=20000)
    tasks: str = Field(min_length=1, max_length=20000)

    @model_validator(mode="after")
    def unique_sources(self):
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("specification source IDs must be unique")
        return self


def validate_sources(bundle, scope):
    if bundle.source_digest != scope["source_digest"] or set(bundle.requirement_ids) != {
        source["id"] for source in scope["sources"]
    }:
        raise ValueError("specification must bind every exact original source")


def validate_mapping(bundle, design, scope, selection):
    from workbench.planning.feature_planner import feature_design_errors

    validate_sources(bundle, scope)
    errors = feature_design_errors(design, scope, selection)
    if errors:
        raise ValueError("specification mapping failed: " + "; ".join(errors))
    return {
        "source_digest": bundle.source_digest,
        "requirement_ids": bundle.requirement_ids,
        "task_ids": [module.id for module in design.outline.modules],
        "authority": "FeatureDesign",
        "execution_authorized": False,
    }
