import pytest
from pydantic import ValidationError

from workbench.domain import FieldSpec, Plan, ProjectInput, ResumeInput, RunInput, digest
from workbench.settings import ROOT, Settings


@pytest.mark.parametrize("value", ["", "   ", "a" * 201])
def test_bad_title(value):
    with pytest.raises(ValidationError):
        ProjectInput(title=value)


def test_role_not_user_controlled():
    with pytest.raises(ValidationError):
        RunInput.model_validate({"requirement": "x", "role": "system"})


@pytest.mark.parametrize("value", ["true", "false", 1, 0, None])
def test_strict_approval(value):
    with pytest.raises(ValidationError):
        ResumeInput(gate_id="a" * 64, action="approve", approved=value)


@pytest.mark.parametrize("name", ["../../x", "id", "owner_id", "class", "BadName"])
def test_reserved_fields(name):
    with pytest.raises(ValidationError):
        FieldSpec(name=name, kind="text")


def test_digest_canonical():
    assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})


def test_path_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = Settings(data_dir="local-data", _env_file=None)
    assert settings.data_dir == ROOT / "local-data"


def test_three_env_names(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "BASE_URL=https://example.test/v1\nAPI_KEY=never-print\nMODE=test-model\n", encoding="utf-8"
    )
    settings = Settings(_env_file=env)
    settings.require_model()
    assert settings.model == "test-model"
    assert "never-print" not in repr(settings)


def test_remote_plain_http_rejected():
    with pytest.raises(ValueError):
        Settings(
            base_url="http://example.test/v1", api_key="x", model="x", _env_file=None
        ).require_model()


def test_plan_duplicate_and_scope(plan):
    data = plan.model_dump()
    data["entities"] *= 2
    with pytest.raises(ValidationError):
        Plan.model_validate(data)
