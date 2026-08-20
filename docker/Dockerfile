FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Only gettext is needed at runtime (manage.py compilemessages). psycopg2-binary
# ships prebuilt wheels, so no build-essential/libpq-dev compile toolchain.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Sync deps before copying the rest of the app so this layer stays cached
# across code-only changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --home-dir /app --no-create-home app && \
    chmod +x docker/entrypoint.sh && \
    mkdir -p logs staticfiles media && \
    chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["./docker/entrypoint.sh"]
