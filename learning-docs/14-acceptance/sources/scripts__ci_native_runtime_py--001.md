# scripts/ci_native_runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原框架本身的运行基线验收。** 复制固定原生源码、初始化专用空库，安装并启动后端/前端，执行原框架登录和权限检查。它测原生基线，不代替新增业务模块和独立交付。

**对应关系：** 本机显式原生基线命令 → native_environment/native_frontend → 基线报告。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.native_checks`、`workbench.native_environment`、`workbench.native_frontend`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L25–L86）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L39按`args.frontend and args.template == "yudao-vben"`分支；L50按`not isinstance(token, str) or len(token) < 10`分支；L51抛异常，停止当前正常路径；L65按`args.frontend`分支；L86抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`Path`、`parser.parse_args`、`Path("reports/native").resolve`、`reports.mkdir`、`copy_source`、`native_environment`、`bootstrap_database`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L90。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3668`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0c431907c32fdae222553b76a0c25953d6aaa4515ea2b4afcbaa42a7e13d4bd0"} -->
````python
# scripts/ci_native_runtime.py
"""Native baseline acceptance against empty test databases, not generated-module acceptance."""

import argparse
import os
from pathlib import Path

from workbench.filesystem import atomic_text, write_json
from workbench.native_checks import check_native_permissions
from workbench.native_environment import (
    bootstrap_database,
    copy_source,
    install_backend,
    login,
    native_environment,
    running_backend,
)
from workbench.native_frontend import (
    browser_check,
    build_frontend,
    frontend_environment,
    frontend_preview,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--source", type=Path, default=Path(".native/source"))
    parser.add_argument("--output", type=Path, default=Path(".native/product"))
    parser.add_argument("--frontend-source", type=Path, default=Path(".native/frontend"))
    parser.add_argument("--frontend", action="store_true")
    args = parser.parse_args()
    reports = Path("reports/native").resolve()
    reports.mkdir(parents=True, exist_ok=True)
    url = os.environ["NATIVE_TEST_DATABASE_URL"]
    copy_source(args.source, args.output)
    backend = args.output / "backend" if args.template == "fastapiadmin" else args.output
    frontend = args.output / "frontend/web"
    if args.frontend and args.template == "yudao-vben":
        frontend = args.output.parent / "frontend-product"
        copy_source(args.frontend_source, frontend)
    env = native_environment(
        args.template, backend, url, 8001 if args.template == "fastapiadmin" else 48080
    )
    try:
        bootstrap_database(args.template, backend, url)
        install_backend(args.template, backend, reports, navigation_api_only=not args.frontend)
        with running_backend(args.template, backend, env, reports) as (base_url, _):
            token = login(args.template, base_url)
            if not isinstance(token, str) or len(token) < 10:
                raise AssertionError("Native login did not return an access token")
            write_json(
                reports / "baseline.json",
                {
                    "template": args.template,
                    "database": "postgresql",
                    "native_login": True,
                    "server_started": True,
                    "generated_runtime_verified": False,
                },
            )
            permissions = check_native_permissions(args.template, base_url, token)
            write_json(reports / "permissions.json", permissions)
            print("Original native backend: login and role permissions PASS")
            if args.frontend:
                front_env = frontend_environment(args.template, base_url)
                build_frontend(args.template, frontend, front_env, reports)
                with frontend_preview(args.template, frontend, front_env, reports) as front_url:
                    browser_check(args.template, front_url, reports)
            write_json(
                reports / "acceptance.json",
                {
                    "template": args.template,
                    "scope": "original-native-baseline",
                    "backend_login": True,
                    "native_permissions": True,
                    "frontend_browser": args.frontend,
                    "generated_runtime_verified": False,
                },
            )
    except Exception as exc:
        atomic_text(
            reports / "failure.log",
            type(exc).__name__ + ": " + str(exc) + "\n" + getattr(exc, "log", ""),
        )
        raise


if __name__ == "__main__":
    main()
````
