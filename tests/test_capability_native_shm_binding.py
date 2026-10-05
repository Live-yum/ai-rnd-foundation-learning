"""Synthetic admission binding checks; no live shared-memory certificate."""

import pytest
from capability_dependency_fixtures import container_binding, profile_record

from workbench.capability_execution import require_profile_container_binding


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.pop("shared_memory"),
        lambda value: value.update(profile="module-container-unprivileged-v1"),
        lambda value: value["shared_memory"].update(ipc_mode="host"),
        lambda value: value["shared_memory"].update(ipc_mode="shareable"),
        lambda value: value["shared_memory"].update(size_bytes=67108864.0),
        lambda value: value["shared_memory"].update(size_bytes=True),
        lambda value: value["shared_memory"].update(size_bytes=67108865),
        lambda value: value["shared_memory"].update(extra=True),
    ],
)
def test_native_image_cannot_downgrade_or_drop_private_memory_binding(mutation):
    record = profile_record(template="fastapiadmin")
    evidence = container_binding(record)
    assert require_profile_container_binding(record, evidence) is evidence
    mutation(evidence)
    with pytest.raises(ValueError, match="private shared memory"):
        require_profile_container_binding(record, evidence)


def test_ordinary_profile_does_not_acquire_native_shared_memory():
    record = profile_record()
    evidence = container_binding(record)
    assert "shared_memory" not in evidence
    assert require_profile_container_binding(record, evidence) is evidence
