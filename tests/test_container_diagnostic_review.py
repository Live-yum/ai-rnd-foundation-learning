"""Independent bounded-diagnostic regressions; no container execution."""

import json

import pytest

from scripts import daytona_capability_profile as profile
from tests.test_daytona_capability_profile import (  # noqa: F401
    SANDBOX,
    execution_inspection,
    inspection,
)
from workbench.capability_isolation import ContainerInspectionRejected


def test_instance_shadowed_allowlists_cannot_release_strings():
    error = ContainerInspectionRejected("secret message", category="resource_limits")
    error._NETWORK_MODES = {"secret network"}
    error._facts = {"network_mode": "secret network", "memory": "secret memory"}
    result = ContainerInspectionRejected.diagnostic(error)
    assert result == {
        "container_rejection": "resource_limits",
        "network_mode": "other",
        "memory": None,
    }
    error._CATEGORIES = {"secret category"}
    error._category = "secret category"
    assert ContainerInspectionRejected.diagnostic(error) == {}


@pytest.mark.parametrize("facts", [None, [], "memory secret", 123, True])
def test_mutated_malformed_facts_preserve_only_finite_category(facts):
    error = ContainerInspectionRejected("secret message", category="resource_limits")
    error._facts = facts
    assert ContainerInspectionRejected.diagnostic(error) == {
        "container_rejection": "resource_limits"
    }


def test_all_diagnostic_fields_are_bounded_and_type_strict():
    error = ContainerInspectionRejected(
        "secret message",
        category="resource_limits",
        facts={
            **dict.fromkeys(ContainerInspectionRejected._NUMBERS, -(2**63)),
            **dict.fromkeys(ContainerInspectionRejected._FLAGS, False),
            "network_mode": "host",
            "unknown": "secret",
        },
    )
    result = error.diagnostic()
    assert len(json.dumps(result)) < 1500
    assert "secret" not in json.dumps(result)
    for name in ContainerInspectionRejected._NUMBERS:
        for value in [True, 1.0, 2**63, -(2**63) - 1, "secret"]:
            error._facts[name] = value
            assert error.diagnostic()[name] is None


@pytest.mark.parametrize("case", ["binary_mounts", "runner_bridge"])
def test_malformed_rejected_facts_do_not_replace_trusted_category(request, case):
    directory, _, inner, _ = request.getfixturevalue("execution_inspection")
    if case == "binary_mounts":
        inner["Mounts"] = [{"Type": "bind", "Destination": [], "Source": "secret", "RW": False}]
    else:
        inner["bridge_inspect"][0]["Driver"] = "unexpected"
        inner["bridge_inspect"][0]["IPAM"] = {"Config": [{"Subnet": ["secret"]}]}
    with pytest.raises(ContainerInspectionRejected) as caught:
        profile.inspect_created_sandbox(directory, SANDBOX, require_resources=True)
    diagnostic = caught.value.diagnostic()
    assert diagnostic["container_rejection"] == case
    assert "secret" not in json.dumps(diagnostic)
