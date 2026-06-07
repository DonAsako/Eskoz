# Themes

Eskoz separates presentation from the core through a theming system. Themes live
in the `themes/` directory; the active one is selected with the `THEME`
environment variable (default: `Eskoz`).

## List available themes

```sh
python3 manage.py list_themes
```

Example output:

```text
Name                      Path                                                         Active
---------------------------------------------------------------------------------------------
Eskoz                     /Eskoz/themes/Eskoz                                          Yes

Successfully listed 1 theme(s).
```

## Create a new theme

From the default structure:

```sh
python3 manage.py create_theme MyNewTheme
```

This generates the necessary folders and files under `themes/`.

Based on an existing theme (e.g. `Eskoz`):

```sh
python3 manage.py create_theme MyNewTheme Eskoz
```

This copies all templates and static files from the base theme.

Once created, customize:

- HTML templates in `templates/`
- Styles and scripts in `static/`

See the [Django Template Language documentation](https://docs.djangoproject.com/en/5.2/ref/templates/language/)
for template syntax.

## Apply a theme

Set it in `.env`:

```ini
THEME=MyNewTheme
```

Then restart the app so the change takes effect:

=== "Docker"
    ```sh
    docker compose -f docker/docker-compose.yml up --build -d
    ```

=== "Bare metal"
    ```sh
    sudo systemctl restart eskoz
    ```

Your new theme should now be visible on the site.
