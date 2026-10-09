"""Independent project obligations; never a replacement for a model-generated Plan."""

import json
from dataclasses import dataclass
from pathlib import Path

from workbench.domain import FieldRequirement, Plan, digest
from workbench.settings import ROOT

CASE_IDS = ("reading-shelf", "stock-purchasing", "facilities-ops")
CASE_ROOT = ROOT / "examples/acceptance"
FIELD_OBLIGATION_KEYS = frozenset(FieldRequirement.model_fields) - {"entity", "field"}
MISSING = object()


def obligation_value(attribute, value):
    """Describe one source-authored field mismatch without exporting arbitrary text."""
    if value is MISSING:
        return {"type": "missing"}
    if value is None or type(value) is bool:
        return value
    if type(value) is int and -(2**31) <= value <= 2**31 - 1:
        return value
    if (
        attribute == "kind"
        and isinstance(value, str)
        and value in {"text", "integer", "boolean", "date", "datetime", "enum"}
    ):
        return value
    result = {"type": type(value).__name__, "sha256": digest(value)}
    if isinstance(value, (str, list, dict)):
        result["characters" if isinstance(value, str) else "items"] = len(value)
    return result


class AcceptanceFailure(RuntimeError):
    """Static controller codes, with an optional local obligation path."""

    def __init__(self, code, path="", *, attribute=None, expected=None, actual=None):
        self.code, self.path = code, path
        self.contract_difference = (
            {
                "attribute": attribute,
                "expected": obligation_value(attribute, expected),
                "actual": obligation_value(attribute, actual),
            }
            if code == "contract_mismatch" and attribute in FIELD_OBLIGATION_KEYS
            else None
        )
        super().__init__(code + (":" + path if path else ""))


def require(condition, code, path=""):
    if not condition:
        raise AcceptanceFailure(code, path)


@dataclass(frozen=True)
class ProjectCase:
    identity: str
    size: str
    title: str
    requirement: str
    contract: dict
    actors: dict
    fixtures: dict
    expected_checks: tuple[str, ...]
    scenario: tuple[dict, ...]
    browser: tuple[dict, ...]
    source_digest: str


def load_case(identity, root=CASE_ROOT):
    require(identity in CASE_IDS, "unknown_case")
    folder = Path(root) / identity
    document = json.loads((folder / "contract.json").read_text(encoding="utf-8"))
    requirement = (folder / "requirement.md").read_text(encoding="utf-8")
    require(document["id"] == identity, "case_identity")
    require(0 < len(requirement) <= 20000, "requirement_length")
    require(document["size"] in {"small", "medium", "large"}, "case_size")
    require(document["expected_checks"], "missing_scenario_checks")
    require(
        len(set(document["expected_checks"])) == len(document["expected_checks"]),
        "duplicate_scenario_check",
    )
    require(
        [block["id"] for block in document["scenario"]] == document["expected_checks"],
        "scenario_contract_mismatch",
    )
    require(any(block.get("restart") for block in document["scenario"]), "missing_restart")
    require(bool(document["browser"]), "missing_browser_scenario")
    return ProjectCase(
        identity=identity,
        size=document["size"],
        title=document["title"],
        requirement=requirement,
        contract=document["contract"],
        actors=document["actors"],
        fixtures=document["fixtures"],
        expected_checks=tuple(document["expected_checks"]),
        scenario=tuple(document["scenario"]),
        browser=tuple(document["browser"]),
        source_digest=digest({"requirement": requirement, "contract": document}),
    )


def same_obligation(actual, expected):
    """Compare declared values without prescribing model-authored display labels/order."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and same_obligation(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        remaining = list(actual)
        for value in expected:
            found = next(
                (i for i, candidate in enumerate(remaining) if same_obligation(candidate, value)),
                None,
            )
            if found is None:
                return False
            remaining.pop(found)
        return True
    return type(actual) is type(expected) and actual == expected


def require_contract(case, value):
    """Check the delivered model contract against source-authored obligations."""
    plan = Plan.model_validate(value)
    actual = plan.model_dump(mode="json")
    expected = case.contract
    require(not plan.unsupported and not plan.custom_rules, "unexpected_implementation_scope")
    require(plan.data_scope == expected["data_scope"], "contract_mismatch", "data_scope")
    entities = {entity["name"]: entity for entity in actual["entities"]}
    require(set(entities) == set(expected["entities"]), "contract_mismatch", "entities")
    for name, fields in expected["entities"].items():
        found = {field["name"]: field for field in entities[name]["fields"]}
        require(set(found) == set(fields), "contract_mismatch", name + ".fields")
        for field, obligation in fields.items():
            attributes = {
                "searchable": False,
                "filterable": False,
                "date_range": False,
                **obligation,
            }
            for attribute, expected_value in attributes.items():
                actual_value = found[field].get(attribute, MISSING)
                if actual_value is MISSING or not same_obligation(actual_value, expected_value):
                    raise AcceptanceFailure(
                        "contract_mismatch",
                        name
                        + "."
                        + field
                        + ("." + attribute if attribute in FIELD_OBLIGATION_KEYS else ""),
                        attribute=attribute,
                        expected=expected_value,
                        actual=actual_value,
                    )
    if "business" not in expected:
        require(plan.business is None, "contract_mismatch", "business")
    else:
        require(plan.business is not None, "contract_mismatch", "business")
        for key, obligation in expected["business"].items():
            require(
                same_obligation(actual["business"].get(key), obligation),
                "contract_mismatch",
                "business." + key,
            )
    return plan


def require_scenario_checks(case, checks):
    require(
        len(checks) == len(set(checks)) and set(checks) == set(case.expected_checks),
        "incomplete_scenario_evidence",
    )


def suite_cases():
    cases = [load_case(identity) for identity in CASE_IDS]
    require([case.size for case in cases] == ["small", "medium", "large"], "suite_sizes")
    require(
        [len(case.contract["entities"]) for case in cases] == [1, 3, 6],
        "suite_entity_counts",
    )
    return cases
