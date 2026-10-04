# syntax=docker/dockerfile:1
# No candidate source enters this build. Runtime dependencies are built at their
# final paths; the application keeps /tmp noexec and never installs executable code.
ARG UV_IMAGE
ARG NODE_IMAGE
ARG SANDBOX_IMAGE
FROM ${UV_IMAGE} AS uv
FROM ${NODE_IMAGE} AS node
FROM ${SANDBOX_IMAGE} AS foundation
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libseccomp2 procps python3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=uv /uv /uvx /usr/local/bin/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/rnd/browsers \
    PRODUCT_VERIFY_PLAYWRIGHT=/opt/rnd/browser/node_modules/playwright
RUN npm install --prefix /opt/rnd/browser --no-audit --no-fund --package-lock=false playwright@1.56.1 \
    && /opt/rnd/browser/node_modules/.bin/playwright install-deps chromium
ENV UV_CACHE_DIR=/opt/rnd/uv-cache \
    UV_PYTHON_INSTALL_DIR=/opt/rnd/python \
    UV_PYTHON_PREFERENCE=only-managed UV_LINK_MODE=copy UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 DO_NOT_TRACK=1
# Managed interpreter installation is trusted, and never writable by the builder.
RUN uv python install 3.14.7 \
    && mkdir -p /opt/rnd/bin /opt/rnd/control /opt/rnd/runtime /opt/rnd/browsers \
    && chown daytona:daytona /opt/rnd/browsers \
    && ln -s "$(uv python find 3.14.7)" /opt/rnd/bin/python-build
COPY dependency-image.py dependency-build.py /opt/rnd/bin/
USER daytona
RUN /opt/rnd/browser/node_modules/.bin/playwright install chromium

FROM foundation AS dependency-builder
USER 0:0
RUN mkdir -p /opt/rnd/runtime/python-basic/.venv /opt/rnd/build \
    && chown daytona:daytona /opt/rnd/runtime/python-basic/.venv /opt/rnd/build
COPY pyproject.toml uv.lock /opt/rnd/runtime/python-basic/
COPY dependency-inputs.json /opt/rnd/build-inputs.json
USER daytona
WORKDIR /opt/rnd/runtime/python-basic
RUN /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py install --basic --project /opt/rnd/runtime/python-basic \
    && /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py collect \
        --inputs /opt/rnd/build-inputs.json --output /opt/rnd/build/runtime-inputs.json

FROM foundation
USER 0:0
COPY --from=dependency-builder --chown=0:0 /opt/rnd/runtime/python-basic/ /opt/rnd/runtime/python-basic/
COPY --from=dependency-builder --chown=0:0 /opt/rnd/build/runtime-inputs.json /opt/rnd/runtime-inputs.json
# Data-only traversal validates all links/hardlinks before no-follow sealing.
RUN chmod 0755 /opt/rnd /opt/rnd/control /opt/rnd/runtime \
    && /usr/bin/python3 -I -S /opt/rnd/bin/dependency-image.py create \
        --profile python-basic --inputs /opt/rnd/runtime-inputs.json
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
ENTRYPOINT []
CMD []
WORKDIR /opt/rnd/control
USER 0:0
