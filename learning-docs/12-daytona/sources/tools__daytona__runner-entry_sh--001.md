# tools/daytona/runner-entry.sh · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Runner启动顺序与退出清理。** 在DinD完成命名空间准备后，仅启动Unix socket上的本机Docker；限时检测daemon就绪再启动Runner，TERM/INT或Runner退出时清理子进程。没有远程Docker或云端回退。

**对应关系：** runner.Dockerfile → dind → runner-entry.sh → dockerd就绪 → 固定版本Runner。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/runner-entry.sh`；**本文件共有 1 段**。本段覆盖源文件 L1–L32。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`878`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/runner-entry.sh", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e23371e723104b5dbf82db81b50389ca3d6ba2dc8b331840e714b88b4c774538"} -->
````bash
# tools/daytona/runner-entry.sh
#!/bin/sh
# Local DinD only; never listen on a TCP socket or inherit a remote Docker context.
set -eu
export DOCKER_HOST=unix:///var/run/docker.sock
unset DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH
dockerd --host=unix:///var/run/docker.sock &
daemon_pid=$!
runner_pid=
cleanup() {
    if [ -n "$runner_pid" ]; then kill -TERM "$runner_pid" 2>/dev/null || true; fi
    kill -TERM "$daemon_pid" 2>/dev/null || true
    wait "$daemon_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
attempt=0
until docker info >/dev/null 2>&1; do
    if ! kill -0 "$daemon_pid" 2>/dev/null || [ "$attempt" -ge 60 ]; then
        echo "Local Docker daemon did not become ready" >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 1
done
/usr/local/bin/daytona-runner &
runner_pid=$!
set +e
wait "$runner_pid"
result=$?
set -e
exit "$result"
````
