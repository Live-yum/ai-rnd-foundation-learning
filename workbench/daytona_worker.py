"""Run the pinned Daytona SDK in an isolated, loopback-only child process."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from workbench.generator import PrerequisiteError
from workbench.local_only import install_loopback_guard
from workbench.tools import clean_env, process_options, stop_process


def run_isolated(product, template, settings):
    payload = {
        "product": str(Path(product).resolve()),
        "template": template,
        "settings": {
            "sandbox_provider": settings.sandbox_provider,
            "daytona_allow_local_execution": settings.daytona_allow_local_execution,
            "daytona_api_url": settings.daytona_api_url,
            "daytona_api_key": settings.daytona_api_key.get_secret_value(),
            "daytona_snapshot": settings.daytona_snapshot,
            "daytona_target": settings.daytona_target,
            "tool_timeout": settings.tool_timeout,
        },
    }
    # A pipe, never argv, a workflow secret, or a report. The child does not
    # inherit cloud credentials, proxy settings or hosted tracing configuration.
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            [sys.executable, "-m", "workbench.daytona_worker"],
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            env=clean_env(),
            **process_options(),
        )
        try:
            process.communicate(
                json.dumps(payload).encode(), timeout=settings.tool_timeout * 12 + 60
            )
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise PrerequisiteError(
                "本机Daytona工作进程超时；检查daytona-verification.json中的沙箱名称并在本机清理"
            ) from None
        if process.returncode:
            output.seek(0, 2)
            output.seek(max(0, output.tell() - 16000))
            error = output.read().decode("utf-8", errors="replace")
            raise PrerequisiteError("本机Daytona未通过：" + settings.redact(error)[-3000:])
    path = Path(product).parent / "daytona-verification.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("passed") is not True or receipt.get("cleanup") != "deleted":
        raise PrerequisiteError("本机Daytona缺少已通过且已清理的验收回执")
    return receipt


def main():
    data = sys.stdin.buffer.read(65537)
    if len(data) > 65536:
        raise ValueError("Daytona控制参数过大")
    payload = json.loads(data)
    install_loopback_guard()
    from workbench.sandbox import _verify_in_daytona, client_for, validate_configuration
    from workbench.settings import Settings

    settings = Settings(_env_file=None, **payload["settings"])
    validate_configuration(settings, payload["template"])
    client = client_for(settings)
    try:
        _verify_in_daytona(payload["product"], payload["template"], settings, client=client)
    except Exception as exc:
        print(settings.redact(str(exc)), file=sys.stderr)
        raise SystemExit(1) from None
    finally:
        if hasattr(client, "close"):
            client.close()


if __name__ == "__main__":
    main()
