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
