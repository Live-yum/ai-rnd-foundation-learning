# workbench/native_frontend.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：完整原生前端构建和浏览器入口。** 按模板选择真实前端根目录和环境，固定包管理器与锁文件安装，执行完整构建/类型检查。preview管理服务端口和生命周期，browser_check启动实际浏览器检查页面，而不是只检查HTML文件存在。

**对应关系：** native_lab/portable → pnpm/Vite/vue-tsc → scripts/native_browser.cjs。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.native_vben`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `frontend_environment`（L18–L63）：接收`template`、`backend_url`、`title`。 控制顺序：L26按`template == "fastapiadmin"`分支；L40按`template != "yudao-vben"`分支；L41抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L27的`{ **common, "VITE_APP_TITLE": title, "VITE_VERSION": "3.0.0", "VITE_PORT": "5173", "VITE_B…`；L42的`{ **common, "VITE_APP_TITLE": title, "VITE_APP_NAMESPACE": "native-lab-vben", # Bound Rust…`。
- `frontend_app`（L66–L68）：接收`template`、`root`。 调用`Path(root).resolve`、`Path`。 返回路径：L68的`root if template == "fastapiadmin" else root / "apps/web-antd"`。
- `build_frontend`（L71–L127）：接收`template`、`root`、`env`、`reports`、`prepared`。 控制顺序：L75按`not (root / "pnpm-lock.yaml").is_file()`分支；L76抛异常，停止当前正常路径；L77按`template == "yudao-vben"`分支；L78按`not prepared`分支；L80按`not (root / ".git").exists()`分支；L110遍历`checks`；L115抛异常，停止当前正常路径；L118按`not (app / "dist/index.html").is_file()`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path(root).resolve`、`Path`、`Path(reports).resolve`、`reports.mkdir`、`frontend_app`、`(root / "pnpm-lock.yaml").is_file`、`ValueError`、`prepare_vben_source`、`(root / ".git").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `frontend_preview`（L131–L171）：接收`template`、`root`、`env`、`reports`。 控制顺序：L156遍历`range(60)`；L157按`process.poll() is not None`分支；L158抛异常，停止当前正常路径；L161按`response.status_code == 200 and "<html" in response.text.lower()`分支；L167抛异常，停止当前正常路径。 调用`frontend_app`、`Path(reports).resolve`、`Path`、`(reports / "frontend-runtime.log").open`、`subprocess.Popen`、`clean_env`、`process_options`、`httpx.Client`、`range`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `browser_check`（L174–L195）：接收`template`、`url`、`reports`。 控制顺序：L177按`not playwright_module.exists()`分支；L178抛异常，停止当前正常路径。 调用`playwright_module.exists`、`ValueError`、`run_command`、`str`、`Path(reports).resolve`、`Path`、`os.environ.get`、`atomic_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/native_frontend.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L195。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7099`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_frontend.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "13e3fc09aeb24d19851530bde86721432d672da98aed8ec1b030791aaf9de46a"} -->
````python
# workbench/native_frontend.py
"""Build the original native application with any generated modules already mounted."""

import json
import os
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

from workbench.filesystem import atomic_text, sha, write_json
from workbench.native_vben import prepare_vben_source
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, run_command, stop_process


def frontend_environment(template, backend_url, title="Native lab"):
    common = {
        "CI": "true",
        "HUSKY": "0",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "NODE_OPTIONS": "--max-old-space-size=4096 --dns-result-order=ipv4first",
    }
    if template == "fastapiadmin":
        return {
            **common,
            "VITE_APP_TITLE": title,
            "VITE_VERSION": "3.0.0",
            "VITE_PORT": "5173",
            "VITE_BASE_URL": "/",
            "VITE_APP_BASE_API": "/api/v1",
            "VITE_API_BASE_URL": backend_url,
            "VITE_API_TIMEOUT": "120000",
            "VITE_ACCESS_MODE": "mixed",
            "VITE_WITH_CREDENTIALS": "false",
            "VITE_LOCK_ENCRYPT_KEY": "native-lab-only",
        }
    if template != "yudao-vben":
        raise ValueError("Unknown native frontend")
    return {
        **common,
        "VITE_APP_TITLE": title,
        "VITE_APP_NAMESPACE": "native-lab-vben",
        # Bound Rust bundler parallelism; give the full Vben graph its native heap budget.
        "RAYON_NUM_THREADS": "2",
        "NODE_OPTIONS": "--max-old-space-size=8192 --dns-result-order=ipv4first",
        "VITE_APP_STORE_SECURE_KEY": "native-lab-only",
        "VITE_BASE": "/",
        "VITE_BASE_URL": backend_url,
        "VITE_GLOB_API_URL": "/admin-api",
        "VITE_NITRO_MOCK": "false",
        "VITE_APP_TENANT_ENABLE": "true",
        "VITE_APP_CAPTCHA_ENABLE": "false",
        "VITE_APP_API_ENCRYPT_ENABLE": "false",
        "VITE_APP_BAIDU_CODE": "",
        "VITE_ROUTER_HISTORY": "hash",
        "VITE_PWA": "false",
        "VITE_ARCHIVER": "false",
        "VITE_COMPRESS": "none",
        "VITE_UPLOAD_TYPE": "server",
    }


def frontend_app(template, root):
    root = Path(root).resolve()
    return root if template == "fastapiadmin" else root / "apps/web-antd"


def build_frontend(template, root, env, reports, *, prepared=False):
    root, reports = Path(root).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    app = frontend_app(template, root)
    if not (root / "pnpm-lock.yaml").is_file():
        raise ValueError("Native frontend lockfile is required")
    if template == "yudao-vben":
        if not prepared:
            prepare_vben_source(root, reports)
        elif not (root / ".git").exists():
            run_command(["git", "init", "--quiet", "--template=", str(root)], root, 30)
        # Vben's own loadAndConvertEnv / runtime-config plugin reads dotenv files,
        # not process.env. Persist only explicitly public VITE_* values in the
        # disposable workspace; never copy platform or database credentials.
        public = {key: value for key, value in env.items() if key.startswith("VITE_")}
        body = (
            "\n".join(f"{key}={json.dumps(value)}" for key, value in sorted(public.items())) + "\n"
        )
        atomic_text(app / ".env.production", body)
        atomic_text(app / ".env.production.example", body)
        write_json(reports / "frontend-public-config.json", public)
    # Native Vite plugins produce auto-imports/components declarations on first build.
    # Checking a pristine checkout before generating them yields false missing-name errors.
    # Type checking remains mandatory, AFTER deterministic generation; no errors are ignored.
    checks = [
        (
            "install",
            [
                "pnpm",
                "install",
                "--frozen-lockfile",
                *(["--offline"] if os.environ.get("RND_OFFLINE_TOOLS") == "1" else []),
            ],
            root,
        ),
        ("build", ["pnpm", "exec", "vite", "build", "--mode", "production"], app),
        ("typecheck", ["pnpm", "exec", "vue-tsc", "--noEmit", "--skipLibCheck"], app),
    ]
    evidence = []
    for name, command, cwd in checks:
        try:
            result = run_command(command, cwd, 900, env, heartbeat=f"native-frontend-{name}")
        except Exception as exc:
            atomic_text(reports / f"frontend-{name}.log", getattr(exc, "log", str(exc)))
            raise
        atomic_text(reports / f"frontend-{name}.log", result["log"])
        evidence.append({"name": name, "command": command, "returncode": 0})
    if not (app / "dist/index.html").is_file():
        raise ValueError("Frontend build did not produce dist/index.html")
    write_json(
        reports / "frontend-build.json",
        {
            "checks": evidence,
            "lock_sha256": sha(root / "pnpm-lock.yaml"),
            "scope": "native-application",
        },
    )


@contextmanager
def frontend_preview(template, root, env, reports):
    app, reports = frontend_app(template, root), Path(reports).resolve()
    url = "http://127.0.0.1:5173"
    command = [
        "pnpm",
        "exec",
        "vite",
        "preview",
        "--host",
        "127.0.0.1",
        "--port",
        "5173",
        "--strictPort",
    ]
    log = (reports / "frontend-runtime.log").open("ab")
    process = subprocess.Popen(
        command,
        cwd=app,
        env=clean_env(env),
        stdout=log,
        stderr=subprocess.STDOUT,
        **process_options(),
    )
    try:
        with httpx.Client(trust_env=False, timeout=3) as client:
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError("Frontend preview exited")
                try:
                    response = client.get(url)
                    if response.status_code == 200 and "<html" in response.text.lower():
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Frontend preview never became ready")
        yield url
    finally:
        stop_process(process)
        log.close()


def browser_check(template, url, reports):
    executable = ROOT / "scripts/native_browser.cjs"
    playwright_module = ROOT / ".native/browser/node_modules/playwright"
    if not playwright_module.exists():
        raise ValueError("Install the pinned Playwright tooling described in the handbook")
    result = run_command(
        [
            "node",
            str(executable),
            template,
            url,
            str(Path(reports).resolve()),
            str(playwright_module),
        ],
        ROOT,
        180,
        {
            "NODE_OPTIONS": "--dns-result-order=ipv4first",
            "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
        },
    )
    atomic_text(Path(reports) / "browser.log", result["log"])
````
