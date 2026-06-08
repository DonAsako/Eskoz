# Themes

Eskoz separates presentation from the core through a theming system. Themes live
in the `themes/` directory; the active one is selected with the `THEME`
environment variable (default: `Eskoz`).

Django looks for templates in the active theme's `templates/` directory **first**,
then falls back to the core app templates. Static files (CSS, JS) are collected
from the active theme's `static/` directory.

## List available themes

```sh
python manage.py list_themes
```

```text
Name                      Path                                            Active
--------------------------------------------------------------------------------
Eskoz                     /opt/eskoz/app/themes/Eskoz                    Yes

Successfully listed 1 theme(s).
```

## Switch themes

Set `THEME` in `.env` to the name of any theme in the `themes/` directory, then
restart the app:

=== "Docker"
    ```sh
    docker compose -f docker/docker-compose.yml up --build -d
    ```

=== "Bare metal"
    ```sh
    sudo systemctl restart eskoz
    ```

## Create a theme

See the full guide: **[Creating a theme](theme-creation.md)**.

The short version:

```sh
# Scaffold from scratch
python manage.py create_theme MyTheme

# Copy an existing theme and rename
python manage.py create_theme MyTheme Eskoz
```

Theme names may only contain letters (`A–Z`, `a–z`) and underscores (`_`).
