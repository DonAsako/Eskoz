FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gettext \
        curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

COPY . .

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --home-dir /app --no-create-home app && \
    chmod +x docker/entrypoint.sh && \
    mkdir -p logs staticfiles media && \
    chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["./docker/entrypoint.sh"]
