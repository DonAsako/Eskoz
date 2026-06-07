# Installation

There are two supported ways to run Eskoz:

- **[With Docker](../deployment/docker.md)** — recommended; everything (app,
  PostgreSQL, reverse proxy with automatic HTTPS) is wired up for you.
- **[On bare metal](../deployment/baremetal.md)** — you run Gunicorn, PostgreSQL
  and a reverse proxy yourself.

Both share the same first steps: get the code and create a `.env` file.

## 1. Clone the repository

```sh
git clone git@github.com:DonAsako/eskoz.git
cd eskoz
```

## 2. Create your environment file

```sh
cp .env.example .env
```

Then edit `.env` to match your environment. Every variable is documented in
[Configuration](configuration.md).

!!! tip "Generate a secret key"
    Never reuse the example secret key. Generate a fresh one:
    ```sh
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```

## Requirements

=== "Docker"
    - Docker
    - Docker Compose

=== "Bare metal"
    - Python 3.13
    - PostgreSQL 16
    - `gettext` (for compiling translations)
    - A reverse proxy (Nginx or Caddy)

Next: head to [Configuration](configuration.md), then pick a deployment guide.
