import uuid

import pytest

from workbench.domain import Patches, Plan, Requirement
from workbench.settings import Settings
from workbench.store import Store


@pytest.fixture
def settings(tmp_path):
    return Settings(data_dir=tmp_path / "state", install_products=False, _env_file=None)


@pytest.fixture
def store(settings):
    value = Store(settings)
    value.migrate()
    yield value
    value.engine.dispose()


@pytest.fixture
def plan():
    return Plan.model_validate(
        {
            "title": "任务管理",
            "data_scope": "per_user",
            "acceptance": ["CRUD 和两用户隔离"],
            "entities": [
                {
                    "name": "task",
                    "description": "任务",
                    "fields": [
                        {"name": "title", "kind": "text", "max_length": 80},
                        {"name": "priority", "kind": "integer"},
                        {"name": "done", "kind": "boolean"},
                    ],
                }
            ],
        }
    )


def requirement(questions=None, scope="per_user"):
    return Requirement(
        summary="任务管理",
        users=["个人用户"],
        data_scope=scope,
        features=["CRUD"],
        acceptance=["CRUD 与数据隔离"],
        questions=questions or [],
    )


class FixtureGateway:
    """Explicit test double: never used by rnd start or live mode."""

    def __init__(self, plan, require_question=False, fail_first_code=False):
        self.plan = plan
        self.require_question = require_question
        self.fail_first_code = fail_first_code
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is Requirement:
            return requirement(
                ["谁使用？"] if self.require_question and key == "requirement:1" else []
            )
        if schema is Plan:
            return self.plan
        if schema is Patches:
            content = "def validate(entity, data):\n    if entity == 'task' and data['priority'] < 0:\n        raise ValueError('priority must be nonnegative')\n"
            if self.fail_first_code and key == "coding:0":
                content = "def validate(entity, data):\n    return None\n"
            return Patches.model_validate(
                {
                    "explanation": "test fixture rule",
                    "patches": [
                        {
                            "path": "custom_rules.py",
                            "before_sha256": payload["context"]["files"]["custom_rules.py"][
                                "sha256"
                            ],
                            "content": content,
                        }
                    ],
                }
            )
        raise AssertionError(schema)


def new_run(store, template="python-basic"):
    project = store.create_project("task", str(uuid.uuid4()))
    return store.create_run(
        project["id"], {"requirement": "个人任务 CRUD", "template": template}, str(uuid.uuid4())
    )["run_id"]


def decision(store, run_id, action="approve", text=""):
    pending = store.get_run(run_id)["pending"]
    return store.submit(
        run_id,
        {
            "gate_id": pending["gate_id"],
            "action": action,
            "approved": True if action == "approve" else False if action == "reject" else None,
            "text": text,
        },
        str(uuid.uuid4()),
    )
