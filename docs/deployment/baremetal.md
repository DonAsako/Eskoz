# Deploy on bare metal

This guide runs Eskoz directly on a Linux host: PostgreSQL for the database,
Gunicorn to serve the app, `systemd` to keep it running, and a reverse proxy
(Nginx in the example, Caddy as an alternative) in front.

It mirrors exactly what the Docker entrypoint does — wait for the DB, migrate,
collect static, compile translations, then start Gunicorn — just done by hand.

!!! info "Assumptions"
    A Debian/Ubuntu host with `sudo`, Python 3.13, and a domain pointing at the
    server. Adjust package commands for other distributions.

## 1. System dependencies

```sh
sudo apt update
sudo apt install -y python3.13 python3.13-venv git gettext \
    postgresql nginx
```

`gettext` is required for `manage.py compilemessages`.

## 2. Create a service user

Run the app under a dedicated, unprivileged user:

```sh
sudo useradd --system --create-home --home-dir /opt/eskoz --shell /bin/bash eskoz
```

## 3. PostgreSQL

Create the database and role (match these to your `.env`):

```sh
sudo -u postgres psql <<'SQL'
CREATE DATABASE eskoz;
CREATE USER eskoz WITH PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE eskoz TO eskoz;
ALTER DATABASE eskoz OWNER TO eskoz;
SQL
```

## 4. Get the code and install dependencies

```sh
sudo -u eskoz -i
git clone https://github.com/DonAsako/eskoz.git /opt/eskoz/app
cd /opt/eskoz/app

python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/production.txt
```

## 5. Configure `.env`

```sh
cp .env.example .env
```

Edit `.env` for a bare-metal install — note `DB_HOST=localhost`:

```ini
DEBUG=0
DJANGO_SECRET_KEY=<generate one, see below>
DJANGO_ALLOWED_HOSTS=example.com
ADMIN_URL=admin
THEME=Eskoz
LANGUAGE_CODE=fr

POSTGRES_DB=eskoz
POSTGRES_USER=eskoz
POSTGRES_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=5432
```

Generate the secret key:

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

See [Configuration](../getting-started/configuration.md) for every variable.

## 6. Initialize the application

With the virtualenv active and `DJANGO_SETTINGS_MODULE` pointing at production:

```sh
export DJANGO_SETTINGS_MODULE=eskoz.settings.production
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages
python manage.py createsuperuser
```

Exit the `eskoz` shell when done: `exit`.

## 7. Run Gunicorn under systemd

Create `/etc/systemd/system/eskoz.service`:

```ini
[Unit]
Description=Eskoz (Gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=eskoz
Group=eskoz
WorkingDirectory=/opt/eskoz/app
Environment=DJANGO_SETTINGS_MODULE=eskoz.settings.production
ExecStart=/opt/eskoz/app/.venv/bin/gunicorn eskoz.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now eskoz
sudo systemctl status eskoz
```

!!! note
    Other variables (`DJANGO_SECRET_KEY`, database credentials, …) are read from
    `.env` automatically because the working directory is the project root. Only
    `DJANGO_SETTINGS_MODULE` needs to be set in the unit file.

## 8. Reverse proxy

Gunicorn listens on `127.0.0.1:8000`. Put a reverse proxy in front to terminate
TLS and serve static/media files.

Two options are described below — pick **one**:

- **Nginx + Certbot** — the most common setup; Certbot manages the certificates.
- **Caddy** — fewer moving parts; obtains and renews TLS certificates
  automatically out of the box.

=== "Nginx + Certbot"

    Create `/etc/nginx/sites-available/eskoz`:

    ```nginx
    server {
        listen 80;
        server_name example.com;

        location /static/ {
            alias /opt/eskoz/app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /opt/eskoz/app/media/;
            expires 1d;
        }

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

    Enable it and obtain a certificate:

    ```sh
    sudo ln -s /etc/nginx/sites-available/eskoz /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d example.com
    ```

    Certbot rewrites the server block for HTTPS and sets up auto-renewal.

=== "Caddy"

    Caddy obtains and renews TLS certificates automatically — no Certbot needed.

    Install it (official repository on Debian/Ubuntu):

    ```sh
    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt update && sudo apt install -y caddy
    ```

    !!! note "Replacing Nginx"
        If you installed Nginx in step 1, stop it first so Caddy can bind ports
        80/443: `sudo systemctl disable --now nginx`.

    Replace `/etc/caddy/Caddyfile` with:

    ```caddy
    {
        email you@example.com
    }

    example.com {
        encode zstd gzip

        handle_path /static/* {
            root * /opt/eskoz/app/staticfiles
            file_server
        }
        handle_path /media/* {
            root * /opt/eskoz/app/media
            file_server
        }
        handle {
            reverse_proxy 127.0.0.1:8000 {
                header_up X-Forwarded-Proto {scheme}
            }
        }
    }
    ```

    Reload Caddy:

    ```sh
    sudo systemctl reload caddy
    ```

    !!! tip "Same as the Docker setup"
        This mirrors the `CaddyFile` shipped for Docker Compose — the bundled
        stack already uses Caddy as its reverse proxy.

!!! warning "`SECURE_SSL_REDIRECT`"
    Production settings enable `SECURE_SSL_REDIRECT` and HSTS, and trust the
    `X-Forwarded-Proto` header. Make sure your proxy sets that header (both
    examples above do), otherwise you'll hit a redirect loop.

## Upgrading

```sh
sudo -u eskoz -i
cd /opt/eskoz/app
git pull
source .venv/bin/activate
pip install -r requirements/production.txt
export DJANGO_SETTINGS_MODULE=eskoz.settings.production
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages
exit
sudo systemctl restart eskoz
```
