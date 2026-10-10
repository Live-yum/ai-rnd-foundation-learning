"""Reviewed agent actions are data; neither commands nor verifier replacements."""

from typing import Literal, Protocol

from pydantic import Field, model_validator

from workbench.core.contracts import Contract
from workbench.planning.contracts import CapabilityEdits


class AgentTurn(Contract):
    operation: Literal["edit", "submit"]
    edits: CapabilityEdits | None = None

    @model_validator(mode="after")
    def action_shape(self):
        if (self.operation == "edit") != (self.edits is not None):
            raise ValueError("edit requires files; submit cannot smuggle edits")
        return self


class AgentBudget(Contract):
    max_requests: int = Field(default=16, ge=1, le=64, strict=True)
    max_tokens: int = Field(default=200000, ge=1, le=2000000, strict=True)
    max_cost_usd: float = Field(default=10, gt=0, le=100)
    timeout_seconds: int = Field(default=180, ge=1, le=900, strict=True)


class CodingEnvironment(Protocol):
    def write(self, edits: CapabilityEdits) -> None: ...
    def snapshot(self, paths: list[str]) -> dict[str, str]: ...
