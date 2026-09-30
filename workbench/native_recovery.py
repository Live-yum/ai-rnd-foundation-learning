"""Identity-bound native validation checkpoints; never re-bootstrap a retained database."""

import json
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.native_environment import checked_database


class NativeIntegrityError(PrerequisiteError):
    """An uncertain edit must not become a trusted retry checkpoint."""


def identity(template, plan, url, source, frontend_source):
    database = checked_database(url)
    return {
        "template": template,
        "spec_digest": digest(plan.model_dump()),
        "database": digest(
            {"host": database.host, "port": database.port or 5432, "database": database.database}
        ),
        "source": digest(manifest(source)),
        "frontend_source": digest(manifest(frontend_source)) if frontend_source else None,
    }


def save(path, expected, product, targets, *, resumable, stage):
    write_json(
        path,
        {
            "identity": expected,
            "files": manifest(product),
            "targets": targets,
            "resumable": resumable,
            "stage": stage,
        },
    )


def load(path, expected, product):
    path = Path(path)
    if not path.is_file():
        raise PrerequisiteError("原生中断现场缺少安全检查点；保留数据，请检查运行证据")
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("identity") != expected:
        raise PrerequisiteError("原生恢复的设计、数据库或模板来源已改变；保留现场并恢复原配置")
    if state.get("resumable") is not True:
        raise PrerequisiteError(
            "原生生成在不可重放步骤中断；保留数据库和源码，需要检查该阶段后恢复"
        )
    if state.get("files") != manifest(product):
        raise PrerequisiteError("原生中断后源码已被修改；不自动覆盖，先核对恢复检查点")
    return state
