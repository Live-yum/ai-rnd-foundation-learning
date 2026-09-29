"""Structured context and command normalization: user control words are not chat answers."""

import json


def command_word(value: str) -> str:
    return value.strip().strip("\"'“”‘’「」『』`").strip().lower()


def context(store, state, capabilities):
    history = store.messages(state["run_id"])
    # The complete audit trail remains in messages. Retain first goal, structured current
    # requirements, and recent corrections rather than growing raw token history forever.
    human = [row for row in history if row["role"] == "user"]
    return {
        "original_request": human[0]["content"] if human else "",
        "current_requirement": state.get("requirement", {}),
        "recent_user_corrections": [r["content"] for r in human[-8:]],
        "template_capabilities": capabilities,
        "autonomous": store.get_run(state["run_id"])["auto_mode"],
        "policy": "Use prior explicit facts unchanged. Latest explicit correction wins. Never re-ask answered facts.",
    }


def concise_requirements(requirement):
    return json.dumps(requirement, ensure_ascii=False, indent=2)
