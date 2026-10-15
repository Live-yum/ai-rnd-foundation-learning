"""Immutable version manifests and atomic promotion, bound to independent proof.

This journals file candidates, not arbitrary shell side effects. An interrupted
external execution must be cleaned up and verified again by its owner.
"""

import json
from pathlib import Path

from filelock import FileLock

from workbench.acceptance.capability_verification import require_evidence
from workbench.core.contracts import digest
from workbench.filesystem import manifest, write_json


class ProductLedger:
    def __init__(self, directory, plan):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.plan = plan
        self.identity = digest(plan.model_dump())
        self.pointer = self.directory / "current.json"
        self.lock = FileLock(str(self.directory / "promotion.lock"), timeout=0)

    def _load(self):
        value = json.loads(self.pointer.read_text())
        if value["plan_digest"] != self.identity:
            raise ValueError("product ledger belongs to a different plan")
        if manifest(value["product"]) != value["files"]:
            raise ValueError("frozen product version changed")
        return value

    def baseline(self, product):
        with self.lock:
            if self.pointer.exists():
                return self._load()
            value = {
                "version": 0,
                "kind": "baseline",
                "plan_digest": self.identity,
                "source_digest": self.plan.source_digest,
                "product": str(Path(product).resolve()),
                "files": manifest(product),
                "completed_tasks": [],
                "implementation_verified": False,
            }
            write_json(self.directory / "v0.json", value)
            write_json(self.pointer, value)
            return value

    def promote(self, product, task, proof, expected_before):
        scenarios = [s for s in self.plan.scenarios if s.id in task.scenarios]
        inventory = manifest(product)
        require_evidence(
            proof,
            source_digest=digest(inventory),
            plan_digest=self.identity,
            scenarios=scenarios,
            selection=self.plan.selection.model_dump(),
            database_tables=self.plan.runtime.database_tables,
        )
        with self.lock:
            current = self._load()
            if task.id in current["completed_tasks"]:
                if (
                    current["task_id"] == task.id
                    and current["files"] == inventory
                    and current["evidence_digest"] == digest(proof)
                ):
                    return current
                raise ValueError("duplicate task has different candidate or evidence")
            if current["files"] != expected_before or not set(task.depends_on) <= set(
                current["completed_tasks"]
            ):
                raise ValueError(
                    "promotion requires the exact verified predecessor and dependencies"
                )
            approved = {t.id: t for t in self.plan.tasks}
            if task.id not in approved or approved[task.id].model_dump() != task.model_dump():
                raise ValueError("task is not part of the approved plan")
            value = {
                "version": current["version"] + 1,
                "kind": "candidate",
                "plan_digest": self.identity,
                "source_digest": self.plan.source_digest,
                "product": str(Path(product).resolve()),
                "files": inventory,
                "before_digest": digest(expected_before),
                "task_id": task.id,
                "completed_tasks": [*current["completed_tasks"], task.id],
                "evidence": proof,
                "evidence_digest": digest(proof),
                "implementation_verified": False,
            }
            # Version receipt first; the atomic pointer is the single publication point.
            write_json(self.directory / f"v{value['version']}.json", value)
            write_json(self.pointer, value)
            return value

    def verified(self, product, proof):
        require_evidence(
            proof,
            source_digest=digest(manifest(product)),
            plan_digest=self.identity,
            scenarios=self.plan.scenarios,
            selection=self.plan.selection.model_dump(),
            database_tables=self.plan.runtime.database_tables,
            aggregate=True,
        )
        with self.lock:
            current = self._load()
            if set(current["completed_tasks"]) != {t.id for t in self.plan.tasks} or current[
                "files"
            ] != manifest(product):
                raise ValueError("aggregate proof must cover every promoted module")
            value = {
                **current,
                "kind": "verified-product",
                "implementation_verified": True,
                "aggregate_evidence": proof,
                "aggregate_evidence_digest": digest(proof),
            }
            write_json(self.directory / "verified.json", value)
            write_json(self.pointer, value)
            return value
