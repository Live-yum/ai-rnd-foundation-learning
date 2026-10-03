# Owned fixed-application profile, based on Daytona's AGPL-3.0 source at the
# exact revision checked by scripts.daytona_capability_profile. Build graph:
# daemon + its pinned terminal assets, real computer-use plugin, then Runner.
# All FROM arguments are official, digest-locked images supplied by the helper.
ARG GO_IMAGE
ARG BUILD_IMAGE
ARG DOCKER_IMAGE
ARG RUNTIME_IMAGE
FROM ${GO_IMAGE} AS go-toolchain
FROM ${BUILD_IMAGE} AS builder
COPY --from=go-toolchain /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}" GOTOOLCHAIN=local GOTELEMETRY=off \
    GOOS=linux GOARCH=amd64 GOMAXPROCS=2 GOFLAGS="-mod=readonly -buildvcs=false -trimpath -p=2"
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates gcc libc6-dev libx11-dev libxtst-dev libpng-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
# Keep upstream's complete workspace and every go.mod/go.sum unchanged. The
# upstream tree omits go.work.sum; the helper seeds it from committed module sums.
# Go may add checksums for the pinned workspace graph, captured with the source.
RUN mkdir -p apps/runner/pkg/daemon/static /out \
    && sha256sum go.work $(find apps libs -name go.mod -o -name go.sum | sort) > /tmp/go-inputs.sha256 \
    && CGO_ENABLED=0 go build -ldflags='-X github.com/daytonaio/daemon/internal.Version=0.190.0' \
        -o apps/runner/pkg/daemon/static/daemon-amd64 ./apps/daemon/cmd/daemon \
    && CGO_ENABLED=1 go build -o apps/runner/pkg/daemon/static/daytona-computer-use ./libs/computer-use \
    && CGO_ENABLED=0 go build -ldflags='-X github.com/daytonaio/runner/internal.Version=0.190.0' \
        -o /out/daytona-runner ./apps/runner/cmd/runner \
    && sha256sum -c /tmp/go-inputs.sha256 \
    && go version -m /out/daytona-runner > /out/runner-build-info.txt \
    && sha256sum /out/daytona-runner apps/runner/pkg/daemon/static/daemon-amd64 \
        apps/runner/pkg/daemon/static/daytona-computer-use > /out/binaries.sha256 \
    && tar --exclude='./apps/runner/pkg/daemon/static/daemon-amd64' \
        --exclude='./apps/runner/pkg/daemon/static/daytona-computer-use' \
        -cf /out/source.tar .
FROM ${DOCKER_IMAGE} AS docker-tools
FROM ${RUNTIME_IMAGE} AS runner
# Retain the ordinary Runner's glibc-compatible runtime and local DinD startup.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl rsync iptables iproute2 kmod procps openssl xz-utils \
    && rm -rf /var/lib/apt/lists/*
COPY --from=docker-tools /usr/local/bin/ /usr/local/bin/
WORKDIR /usr/local/bin
COPY --from=builder --chmod=0755 /out/daytona-runner /usr/local/bin/daytona-runner
COPY --chmod=0755 capability-build/runner-entry.sh /usr/local/bin/rnd-runner-entry.sh
COPY --from=builder /out/source.tar /out/runner-build-info.txt /out/binaries.sha256 /usr/share/daytona-profile/
COPY LICENSE capability-build/NOTICE /usr/share/daytona-profile/
RUN set +e; API_PORT=invalid /usr/local/bin/daytona-runner >/tmp/runner-smoke.log 2>&1; \
    result=$?; set -e; cat /tmp/runner-smoke.log; \
    test "$result" = 2 && grep -q 'Failed to get config' /tmp/runner-smoke.log \
    && rm /tmp/runner-smoke.log
RUN mkdir -p /etc/docker && \
    printf '%s\n' '{"insecure-registries": ["registry:6000"]}' > /etc/docker/daemon.json
ENV DO_NOT_TRACK=1 OTEL_SDK_DISABLED=true DOCKER_HOST=unix:///var/run/docker.sock \
    USE_SNAPSHOT_ENTRYPOINT=false
VOLUME ["/var/lib/docker"]
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD docker info >/dev/null && curl -f http://localhost:3003/
ENTRYPOINT ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"]
