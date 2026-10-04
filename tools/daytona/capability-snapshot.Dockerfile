# Build dependencies are downloaded here, not while executing generated code.
ARG UV_IMAGE
ARG NODE_IMAGE
ARG SANDBOX_IMAGE
FROM ${UV_IMAGE} AS uv
FROM ${NODE_IMAGE} AS node
FROM ${SANDBOX_IMAGE}
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libseccomp2 procps \
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
    UV_PYTHON_PREFERENCE=only-managed \
    UV_LINK_MODE=copy \
    UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 \
    DO_NOT_TRACK=1
WORKDIR /opt/rnd/prewarm
COPY pyproject.toml uv.lock ./
RUN uv python install 3.14.7 && uv sync --locked --no-dev --python 3.14.7 \
    && rm -rf .venv && chown -R daytona:daytona /opt/rnd
USER daytona
RUN /opt/rnd/browser/node_modules/.bin/playwright install chromium
WORKDIR /home/daytona

ENTRYPOINT []
CMD []
# The normal Daytona daemon uses this declared image identity. The application
# guard independently drops to UID/GID 20000 with no capabilities or new privileges.
USER 0:0
RUN mkdir -p /opt/rnd/control && chown 0:0 /opt/rnd /opt/rnd/control \
    && chmod 0755 /opt/rnd /opt/rnd/control
WORKDIR /opt/rnd/control
USER 0:0
