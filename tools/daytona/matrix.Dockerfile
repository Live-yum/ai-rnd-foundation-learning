# Explicit local image preparation. Generated code is executed later without egress.
FROM ghcr.io/astral-sh/uv:0.12.20 AS uv
FROM node:22.23.2-bookworm-slim AS node
FROM daytonaio/sandbox:0.5.0-slim
USER root
COPY --from=uv /uv /uvx /usr/local/bin/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg git redis-server openjdk-17-jdk-headless maven \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && . /etc/os-release && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends postgresql-17 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/rnd/harness /opt/rnd/browser /opt/rnd/prewarm \
    && chown -R daytona:daytona /opt/rnd
ARG PNPM_VERSION=9.15.3
RUN npm install --global pnpm@${PNPM_VERSION}
ENV UV_CACHE_DIR=/opt/rnd/uv-cache \
    UV_PYTHON_INSTALL_DIR=/opt/rnd/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_LINK_MODE=copy \
    UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 \
    DO_NOT_TRACK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/rnd/browsers \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PATH=/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/bin:/bin
COPY --chown=daytona:daytona harness/ /opt/rnd/harness/
COPY --chown=daytona:daytona product/ /opt/rnd/prewarm/product/
COPY --chown=daytona:daytona profile.json warm.py /opt/rnd/
RUN npm install --prefix /opt/rnd/browser --no-audit --no-fund --package-lock=false playwright@1.56.1 \
    && /opt/rnd/browser/node_modules/.bin/playwright install-deps chromium \
    && chown -R daytona:daytona /opt/rnd
USER daytona
WORKDIR /opt/rnd/harness
RUN uv python install 3.14.7 \
    && uv sync --locked --all-extras --no-install-project --python 3.14.7 \
    && /opt/rnd/browser/node_modules/.bin/playwright install chromium \
    && .venv/bin/python /opt/rnd/warm.py \
    && rm -rf /opt/rnd/prewarm
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
WORKDIR /home/daytona
