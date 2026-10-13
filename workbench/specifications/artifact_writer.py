"""Each run and source revision owns its separate document-only workspace."""

import json
from pathlib import Path

from workbench.filesystem import atomic_text, inside, write_json
from workbench.specifications.openspec.cli import ARTIFACTS, SCHEMA

OUTPUTS = {
    "proposal": "proposal.md",
    "specs": "specs/product/spec.md",
    "design": "design.md",
    "tasks": "tasks.md",
}


def initialize_workspace(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    schema = inside(root, "openspec/schemas/" + SCHEMA)
    artifacts = []
    for name in ARTIFACTS:
        atomic_text(
            inside(schema, "templates/" + name + ".md"),
            "# "
            + name
            + "\n\nPreserve exact source IDs. This document grants no execution authority.\n",
        )
        artifacts.append(
            {
                "id": name,
                "generates": OUTPUTS[name],
                "description": "Unapproved " + name,
                "template": name + ".md",
                "instruction": "Document requirements only. Never execute or edit product code.",
                "requires": []
                if name == "proposal"
                else (["proposal"] if name != "tasks" else ["specs", "design"]),
            }
        )
    # JSON is a YAML subset; no model-controlled schema or executable hooks.
    atomic_text(
        inside(schema, "schema.yaml"),
        json.dumps(
            {
                "name": SCHEMA,
                "version": 1,
                "description": "RND document-only specification",
                "artifacts": artifacts,
            }
        ),
    )
    atomic_text(inside(root, "openspec/config.yaml"), "schema: rnd-factory\n")
    return root


def write_artifacts(workspace, bundle):
    change = inside(workspace, "openspec/changes/product")
    for name, output in OUTPUTS.items():
        atomic_text(inside(change, output), getattr(bundle, name))
    write_json(
        inside(change, "source-binding.json"),
        {
            "source_digest": bundle.source_digest,
            "requirement_ids": bundle.requirement_ids,
            "execution_authorized": False,
        },
    )
