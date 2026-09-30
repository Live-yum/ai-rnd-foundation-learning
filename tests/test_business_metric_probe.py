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
        "customers": [
            {"id": "1", "category": "企业"},
            {"id": "2", "category": "企业"},
            {"id": "3", "category": "个人"},
        ],
        "requests": [
            {
                "id": "4",
                "customer_id": "1",
                "request_state": "resolved",
                "created_at": "2026-01-01T00:00:00Z",
                "resolved_at": "2026-01-01T00:01:00Z",
            },
            {
                "id": "5",
                "customer_id": "1",
                "request_state": "resolved",
                "created_at": "2026-01-02T00:00:00Z",
                "resolved_at": "2026-01-02T00:03:00Z",
            },
            {
                "id": "6",
                "customer_id": "3",
                "request_state": "new",
                "created_at": "2026-01-02T00:00:00Z",
                "resolved_at": None,
            },
        ],
    }
    values = {
        "total": {"value": 3},
        "resolved_total": {"value": 2},
        "resolution": {"value": 120, "samples": 2},
        "by_customer": {"groups": [{"key": "1", "count": 2}, {"key": "3", "count": 1}]},
        "daily": {"groups": [{"day": "2026-01-01", "count": 1}, {"day": "2026-01-02", "count": 2}]},
        "customer_total": {"value": 3},
        "customer_categories": {
            "groups": [{"key": "企业", "count": 2}, {"key": "个人", "count": 1}]
        },
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
    assert len(verify_scoped_metrics(client, plan)) == len(plan.business.metrics) == 7


@pytest.mark.parametrize(
    "name,value",
    [
        ("total", {"value": True}),
        ("total", {"value": 2}),
        ("resolved_total", {"value": 3}),
        ("resolution", {"value": 60, "samples": 2}),
        ("resolution", {"value": 120, "samples": 3}),
        ("by_customer", {"groups": [{"key": "other", "count": 3}]}),
        ("customer_categories", {"groups": [{"key": "企业", "count": 3}]}),
        ("daily", {"groups": [{"day": "2026-01-02", "count": 3}]}),
    ],
)
def test_broken_metric_values_do_not_count_as_functional_acceptance(name, value):
    client, plan, values = fixture()
    values[name] = deepcopy(value)
    with pytest.raises(AssertionError):
        verify_scoped_metrics(client, plan)


def test_service_cannot_silently_lose_its_approved_metrics():
    client, plan, values = fixture()
    values.pop("resolution")
    with pytest.raises(AssertionError, match="Metric set"):
        verify_scoped_metrics(client, plan, "service")


def test_metric_oracle_accepts_provider_names_and_yudao_wire_format():
    client, plan, values = fixture()
    for number, metric in enumerate(plan.business.metrics):
        values[f"provider_metric_{number}"] = values.pop(metric.name)
        metric.name = f"provider_metric_{number}"
    original_rows = client.rows
    from workbench.business_probe import wire_name

    client.template = "yudao-vben"
    client.rows = lambda entity, **kwargs: [
        {wire_name(client.template, key): value for key, value in row.items()}
        for row in original_rows(entity)
    ]
    assert len(verify_scoped_metrics(client, plan)) == len(values)
