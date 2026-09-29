"""Pinned Aider API/CLI in its own Python 3.12 process. No model or network permission."""

import contextlib
import json
import os
import socket
import sys
from pathlib import Path


def denied(*args, **kwargs):
    raise OSError("RND offline Aider worker does not allow network calls")


def byte_count(self, text):
    # Conservative budget independent of tokenizer downloads. It is NOT a model token count.
    return len((text if isinstance(text, str) else json.dumps(text)).encode("utf-8"))


def main():
    operation, source, argument, output = sys.argv[1:5]
    source, output = Path(source).resolve(), Path(output).resolve()
    os.chdir(source)
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.create_connection = denied
    socket.getaddrinfo = denied
    if operation == "map":
        from aider.io import InputOutput
        from aider.repomap import RepoMap

        rows = json.loads(Path(argument).read_text(encoding="utf-8"))
        model = type("ByteBudget", (), {"token_count": byte_count})()
        with contextlib.redirect_stdout(sys.stderr):
            mapper = RepoMap(
                map_tokens=rows["budget"],
                root=str(source),
                main_model=model,
                io=InputOutput(yes=True, pretty=False),
                map_mul_no_files=1,
            )
            result = mapper.get_repo_map([], [str(source / n) for n in rows["files"]]) or ""
        output.write_text(
            json.dumps(
                {
                    "text": result,
                    "engine": "aider-0.86.2-repomap",
                    "budget_unit": "utf8-bytes-conservative",
                }
            ),
            encoding="utf-8",
        )
    elif operation == "apply":
        from aider import models
        from aider.main import main as aider_main

        models.Model.token_count = byte_count
        config, env = output.parent / "empty.yml", output.parent / "empty.env"
        config.write_text("{}\n", encoding="utf-8")
        env.write_text("", encoding="utf-8")
        args = [
            "--model",
            "gpt-4o",
            "--edit-format",
            "diff",
            "--apply",
            argument,
            "--no-git",
            "--yes-always",
            "--no-analytics",
            "--no-check-update",
            "--no-auto-lint",
            "--no-auto-test",
            "--no-show-model-warnings",
            "--no-suggest-shell-commands",
            "--no-auto-commits",
            "--no-dirty-commits",
            "--map-tokens",
            "0",
            "--no-pretty",
            "--no-fancy-input",
            "--config",
            str(config),
            "--env-file",
            str(env),
            "--input-history-file",
            str(output.parent / "input.history"),
            "--chat-history-file",
            str(output.parent / "chat.history"),
            "--llm-history-file",
            str(output.parent / "llm.history"),
            "custom_rules.py",
        ]
        code = aider_main(args)
        if code:
            raise SystemExit(code)
        output.write_text('{"engine":"aider-0.86.2-apply","model_calls":0}', encoding="utf-8")
    else:
        raise ValueError("Unknown fixed worker operation")


if __name__ == "__main__":
    main()
