"""Validated selection uses the same executable catalog exposed by all discovery surfaces."""

from pydantic import BaseModel, ConfigDict, model_validator

from workbench.template_adapters import get_adapter, template_ids

# Compatibility view for integrations that used PAIRS; never a second source of truth.
PAIRS = {template: get_adapter(template).selection_spec() for template in template_ids()}


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "python-basic"
    backend: str = ""
    frontend: str = ""
    database: str = ""

    @model_validator(mode="after")
    def supported(self):
        adapter = get_adapter(self.template)
        self.backend = self.backend or adapter.backend
        self.frontend = self.frontend or adapter.frontends[0]
        self.database = self.database or adapter.databases[0]
        adapter.validate_selection(self.backend, self.frontend, self.database)
        return self

    def capabilities(self):
        return {**get_adapter(self.template).capabilities(), **self.model_dump()}


def options_for_run(run):
    options = dict(run.get("options") or {"template": run["template"]})
    options.pop("allow_custom_extensions", None)
    return Selection.model_validate(options)


def selections():
    return [Selection(template=template).capabilities() for template in template_ids()]
