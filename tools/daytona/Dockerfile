# Build dependencies are downloaded here, not while executing generated code.
FROM ghcr.io/astral-sh/uv:0.12.20 AS uv
FROM daytonaio/sandbox:0.5.0-slim
USER root
COPY --from=uv /uv /uvx /usr/local/bin/
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
WORKDIR /home/daytona
