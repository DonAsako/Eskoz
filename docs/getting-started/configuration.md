# Configuration

Eskoz is configured entirely through environment variables, read from a `.env`
file at the project root (loaded automatically via `python-dotenv` in every
environment). Start from the template:

```sh
cp .env.example .env
```

## Settings modules

Eskoz ships three Django settings modules, selected with `DJANGO_SETTINGS_MODULE`:

| Module                       | Use                          | Database   |
| ---------------------------- | ---------------------------- | ---------- |
| `eskoz.settings.development` | Local development            | SQLite     |
| `eskoz.settings.production`  | Real deployments             | PostgreSQL |
| `eskoz.settings.ci`          | Automated tests in CI        | PostgreSQL |

Docker Compose sets `eskoz.settings.production` for you. On bare metal you set it
yourself (see the [bare metal guide](../deployment/baremetal.md)).

## Variables

### Django

| Variable               | Description                                                     | Example         |
| ---------------------- | --------------------------------------------------------------- | --------------- |
| `DEBUG`                | Enable (`1`) or disable (`0`) Django debug mode.                | `0`             |
| `DJANGO_SECRET_KEY`    | Secret key used for cryptographic signing. **Keep it secret.**  | *(generated)*   |
| `DJANGO_ALLOWED_HOSTS` | Space-separated list of hostnames the site may be served from.  | `example.com`   |
| `ADMIN_URL`            | URL path for the Django admin (avoid the default for security). | `admin`         |
| `THEME`                | Active theme from the `themes/` directory.                      | `Eskoz`         |
| `LANGUAGE_CODE`        | Default language code.                                          | `fr`            |

!!! warning "Production hosts"
    In production, `DJANGO_ALLOWED_HOSTS` must list every domain that serves the
    site. `CSRF_TRUSTED_ORIGINS` is derived automatically as `https://<host>`
    for each entry.

### PostgreSQL

| Variable            | Description           |
| ------------------- | --------------------- |
| `POSTGRES_DB`       | Database name.        |
| `POSTGRES_USER`     | Database user.        |
| `POSTGRES_PASSWORD` | Database password.    |

The host and port default to `db:5432` (the Docker service name). On bare metal,
set them explicitly:

| Variable  | Description          | Bare-metal value |
| --------- | -------------------- | ---------------- |
| `DB_HOST` | Database host.       | `localhost`      |
| `DB_PORT` | Database port.       | `5432`           |

### Reverse proxy (Docker / Caddy)

These drive the bundled Caddy container, which obtains TLS certificates
automatically.

| Variable | Description                                  | Example           |
| -------- | -------------------------------------------- | ----------------- |
| `DOMAIN` | Your domain name.                            | `example.com`     |
| `EMAIL`  | Email used for Let's Encrypt SSL certs.      | `you@example.com` |

### Integrations (optional)

| Variable      | Description                                                                 | Example       |
| ------------- | -------------------------------------------------------------------------- | ------------- |
| `NVD_API_KEY` | Raises the rate limit when enriching CVEs from NVD (no key needed to work). | *(unset)*     |

The CVE admin offers a **Fetch from NVD** action (on the changelist and on each
CVE page) that fills the description, CVSS score, dates, affected product and
reference from the [NVD API](https://nvd.nist.gov/developers/vulnerabilities) by
CVE id. It works without any key; the public limit is ~5 requests per 30 s. To
enrich in bulk, request a free key at
[nvd.nist.gov](https://nvd.nist.gov/developers/request-an-api-key) and set it as
`NVD_API_KEY` — it is then used automatically.

## Generating a secret key

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the output into `DJANGO_SECRET_KEY`.
