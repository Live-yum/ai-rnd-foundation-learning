"""Python 3.12 mini-SWE driver. No credentials, shell environment, or product mount.

JSON-line RPC delegates model access and filesystem edits to the platform. The
custom Environment intentionally has no execute-command operation.
"""

import json
import sys
from importlib.metadata import version

if sys.version_info[:2] != (3, 12) or version("mini-swe-agent") != "2.4.6":
    raise RuntimeError("Worker requires reviewed Python 3.12 and mini-swe-agent 2.4.6")

from minisweagent.agents.default import DefaultAgent

LIMIT = 1_200_000


def rpc(operation, payload):
    print(json.dumps({"operation": operation, "payload": payload}), flush=True)
    line = sys.stdin.buffer.readline(LIMIT + 1)
    if not line or len(line) > LIMIT:
        raise ValueError("bounded RPC response missing")
    result = json.loads(line)
    if "error" in result:
        raise ValueError("platform rejected worker operation")
    return result["result"]


class PlatformModel:
    def query(self, messages):
        turn = rpc("model", {"messages": messages})
        return {
            "role": "assistant",
            "content": "structured business-file action",
            "extra": {"actions": [turn], "cost": 0.0},
        }

    def format_message(self, **kwargs):
        return kwargs

    def format_observation_messages(self, message, outputs, template_vars):
        if outputs and outputs[-1].get("submitted"):
            return [
                {
                    "role": "exit",
                    "content": "candidate submitted",
                    "extra": {"exit_status": "Submitted", "submission": "candidate"},
                }
            ]
        return [{"role": "user", "content": json.dumps(outputs)}]

    def get_template_vars(self):
        return {}

    def serialize(self):
        return {"model": "platform-gateway", "billing_authority": "platform-reservations"}


class DaytonaEnvironment:
    def execute(self, action):
        if action.get("operation") not in {"edit", "submit"}:
            raise ValueError("No shell commands or local execution are supported")
        return rpc("environment", action)

    def get_template_vars(self):
        return {"environment": "approved-local-daytona"}

    def serialize(self):
        return {"environment": "platform-daytona-rpc", "local_execution": False}


def main():
    initial = json.loads(sys.stdin.buffer.readline(LIMIT + 1))
    if set(initial) != {"task", "max_steps", "timeout"}:
        raise ValueError("unexpected worker configuration")
    agent = DefaultAgent(
        PlatformModel(),
        DaytonaEnvironment(),
        system_template="Only propose edits to approved business files, then submit. No shell actions.",
        instance_template="{{ task }}",
        step_limit=initial["max_steps"],
        wall_time_limit_seconds=initial["timeout"],
        cost_limit=0,
    )
    result = agent.run(initial["task"])
    print(
        json.dumps(
            {
                "operation": "result",
                "payload": {"exit_status": result.get("exit_status"), "steps": agent.n_calls},
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
