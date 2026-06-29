# Deploy with Docker

This is the recommended way to run Eskoz. The Compose stack provides three
services:

- **db** — PostgreSQL 16, with a persistent volume.
- **web** — the Django app served by Gunicorn (migrations, `collectstatic` and
  translation compilation run automatically on start).
- **caddy** — a reverse proxy that terminates TLS with automatic Let's Encrypt
  certificates and serves `/static` and `/media` directly.

## Prerequisites

- Docker and Docker Compose installed
- A `.env` file at the project root (see [Configuration](../getting-started/configuration.md))
- For HTTPS: a domain whose DNS points at the host, plus `DOMAIN` and `EMAIL` set

## 1. Build and start the stack

```sh
docker compose -f docker/docker-compose.yml up --build -d
```

The `web` container's entrypoint waits for the database, applies migrations,
collects static files and compiles translations before launching Gunicorn — so
the first start may take a moment.

## 2. Create the first admin user

```sh
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

## 3. Update your config

```sh
docker compose -f docker/docker-compose.yml exec web python manage.py config
```

## Using the prebuilt image

Every release is automatically published to the GitHub Container Registry, so you
don't have to build locally. Pull a tagged image:

```sh
docker pull ghcr.io/donasako/eskoz:latest      # or a specific version, e.g. :v0.6.0
```

To run it via Compose, replace the `build:` block of the `web` service with:

```yaml
  web:
    image: ghcr.io/donasako/eskoz:latest
```

## Common operations

| Task                   | Command                                                                   |
| ---------------------- | ------------------------------------------------------------------------- |
| View logs              | `docker compose -f docker/docker-compose.yml logs -f web`                 |
| Run migrations         | `docker compose -f docker/docker-compose.yml exec web python manage.py migrate` |
| Open a Django shell    | `docker compose -f docker/docker-compose.yml exec web python manage.py shell`   |
| Stop the stack         | `docker compose -f docker/docker-compose.yml down`                        |

!!! note "Data persistence"
    Database, static and media files live in named Docker volumes
    (`postgres_data`, `static_volume`, `media_volume`). `down` keeps them; add
    `-v` only if you really want to delete your data.

## Logs and tracebacks

The app logs to two places in production:

- **stdout** — captured by Docker. Use this for a live view, including the full
  traceback of any `500` error:

    ```sh
    docker compose -f docker/docker-compose.yml logs -f web
    ```

- **`logs/django.log`** — `ERROR`-level entries (unhandled exceptions, request
  failures) are also written to a file. The `web` service bind-mounts the host's `logs/` directory to `/app/logs`, so the file survives container restarts and can be read directly on the host:

    ```sh
    tail -n 80 logs/django.log
    ```


!!! warning "Log file ownership"
    The container runs as uid `1000` (the `app` user). For the bind-mounted
    `logs/` directory to be writable, it must be owned by that uid, otherwise
    Django's file handler fails to open `django.log` on startup. If you hit a
    permission error, fix it once on the host:

    ```sh
    sudo rm -f logs/django.log        # drop any root-owned leftover
    sudo chown -R 1000:1000 logs/
    ```
