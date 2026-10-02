# templates/product/start.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 成品自包含入口：在产品目录安装自己的锁定依赖，准备本机SQLite或专用PostgreSQL，执行迁移后启动HTTP服务；不调用模型，不要求原工作台目录。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L21–L92）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L30按`not args.no_install`分支；L32按`not uv`分支；L33抛异常，停止当前正常路径；L35按`selection["database"] == "postgresql"`分支；L39按`selection["database"] == "postgresql" and not env.get("PRODUCT_DATABASE_URL")`分支；L41按`not docker`分支；L42抛异常，停止当前正常路径；L48按`not config.exists()`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`json.loads`、`(ROOT / "selection.json").read_text`、`os.environ.copy`、`shutil.which`、`SystemExit`、`subprocess.run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/product/start.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L96。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3508`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/start.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3fcf43d69fe8b0856d58b84776518f11fff1701d30bfa16f795c4b9d433e0f3a"} -->
````python
# templates/product/start.py
"""One local command after unzip. Creates only its own database volume; never resets data.

python start.py                  # install locked dependencies, init/migrate and serve
python start.py --init-only      # install and apply migrations, do not serve
python start.py --no-install     # use current Python (CI / preinstalled environment)
"""

import argparse
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--init-only", action="store_true")
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()
    selection = json.loads((ROOT / "selection.json").read_text(encoding="utf-8"))
    env = os.environ.copy()
    python = sys.executable
    if not args.no_install:
        uv = shutil.which("uv")
        if not uv:
            raise SystemExit("Install uv first; see README.md")
        cmd = [uv, "sync", "--locked", "--no-dev"]
        if selection["database"] == "postgresql":
            cmd += ["--extra", "postgres"]
        subprocess.run(cmd, cwd=ROOT, check=True)
        python = str(ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
    if selection["database"] == "postgresql" and not env.get("PRODUCT_DATABASE_URL"):
        docker = shutil.which("docker")
        if not docker:
            raise SystemExit(
                "Selected PostgreSQL: start Docker Desktop, or supply PRODUCT_DATABASE_URL for your local database"
            )
        data = ROOT / ".data"
        data.mkdir(exist_ok=True)
        config = data / "deployment.json"
        if not config.exists():
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            value = {
                "password": secrets.token_urlsafe(32),
                "port": port,
                "project": "rnd" + secrets.token_hex(6),
            }
            with config.open("x", encoding="utf-8") as file:
                json.dump(value, file)
            config.chmod(0o600)
        value = json.loads(config.read_text(encoding="utf-8"))
        deployment = data / "deployment.env"
        deployment.write_text(
            f"POSTGRES_PASSWORD={value['password']}\nPG_PORT={value['port']}\nCOMPOSE_PROJECT_NAME={value['project']}\n",
            encoding="utf-8",
        )
        deployment.chmod(0o600)
        subprocess.run(
            [
                docker,
                "--host",
                "npipe:////./pipe/docker_engine"
                if os.name == "nt"
                else "unix:///var/run/docker.sock",
                "compose",
                "--env-file",
                str(deployment),
                "up",
                "-d",
                "--wait",
                "database",
            ],
            cwd=ROOT,
            check=True,
        )
        env["PRODUCT_DATABASE_URL"] = (
            f"postgresql+psycopg://product:{value['password']}@127.0.0.1:{value['port']}/product"
        )
    action = "init" if args.init_only else "start"
    print("Applying versioned migrations; existing data is preserved.", flush=True)
    subprocess.run(
        [python, "manage.py", action, "--port", str(args.port)], cwd=ROOT, env=env, check=True
    )


if __name__ == "__main__":
    main()
````
