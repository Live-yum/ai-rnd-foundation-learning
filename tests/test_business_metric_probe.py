from copy import deepcopy

import pytest

from workbench.business_probe import verify_scoped_metrics
from workbench.domain import Plan
from workbench.settings import ROOT


def fixture():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    rows = {
        "customers": [{"id": "1"}],
        "requests": [
            {
                "id": "2",
                "customer_id": "1",
                "request_state": "resolved",
                "created_at": "2026-01-01T00:00:00Z",
                "resolved_at": "2026-01-01T00:01:00Z",
            }
        ],
    }
    values = {
        "total": {"value": 1},
        "resolution": {"value": 60, "samples": 1},
        "by_customer": {"groups": [{"key": "1", "count": 1}]},
        "daily": {"groups": [{"day": "2026-01-01", "count": 1}]},
        "customer_total": {"value": 1},
    }

    class Client:
        template = "fastapiadmin"
        prefix = "/business"

        def rows(self, entity, **kwargs):
            return rows[entity]

        def call(self, *args, **kwargs):
            return [{"name": name, "value": value} for name, value in values.items()]

    return Client(), plan, values


def test_independent_metric_values_use_authorized_http_rows():
    client, plan, _ = fixture()
    assert len(verify_scoped_metrics(client, plan)) == 5


@pytest.mark.parametrize(
    "name,value",
    [
        ("total", {"value": True}),
        ("total", {"value": 2}),
        ("resolution", {"value": 1, "samples": 1}),
        ("by_customer", {"groups": [{"key": "other", "count": 1}]}),
        ("daily", {"groups": [{"day": "2026-01-02", "count": 1}]}),
    ],
)
def test_broken_metric_values_do_not_count_as_functional_acceptance(name, value):
    client, plan, values = fixture()
    values[name] = deepcopy(value)
    with pytest.raises(AssertionError):
        verify_scoped_metrics(client, plan)
