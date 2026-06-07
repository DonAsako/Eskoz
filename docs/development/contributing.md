# Contributing & releases

Contributions are welcome. This page summarizes the development workflow; the
canonical reference is
[`CONTRIBUTING.md`](https://github.com/DonAsako/eskoz/blob/main/CONTRIBUTING.md)
in the repository.

## Local setup

```sh
git clone git@github.com:DonAsako/eskoz.git
cd eskoz
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements/development.txt
pre-commit install            # installs the pre-commit and commit-msg hooks
```

## Quality checks

Quality is enforced by [pre-commit](https://pre-commit.com/) (Ruff, djLint,
yamllint, gitleaks, gitlint, Django checks). The hooks run on every commit; run
them on demand with:

```sh
pre-commit run --all-files
```

## Running tests

Locally the suite runs on SQLite via the development settings:

```sh
export DJANGO_SETTINGS_MODULE=eskoz.settings.development
export DJANGO_SECRET_KEY=dev-dummy-key
python manage.py test apps.analytics apps.blog apps.core apps.education apps.infosec -t .
```

!!! note "The `-t .` flag"
    It sets the test discovery top-level directory to the repo root so the
    `apps.*.models` packages import under their real dotted path.

In CI, the same suite runs against PostgreSQL using `eskoz.settings.ci`.

## Commit convention

Eskoz uses [Conventional Commits](https://www.conventionalcommits.org/). The
prefix drives automated versioning and the changelog:

| Prefix      | Meaning                          | Version bump |
| ----------- | -------------------------------- | ------------ |
| `feat:`     | A new feature                    | minor        |
| `fix:`      | A bug fix                        | patch        |
| `perf:`     | A performance improvement        | patch        |
| `refactor:` | Code change, no behaviour change | patch        |
| `docs:`     | Documentation only               | none         |
| `chore:`    | Tooling, deps, housekeeping      | none         |

A breaking change (`feat!:` or a `BREAKING CHANGE:` footer) triggers a **major**
bump.

## How releases work

Everything from a merge to a published release is automated:

1. **On every pull request and push to `main`**, the CI workflow runs the
   quality suite and the PostgreSQL test suite.
2. **Versioning is handled by [release-please](https://github.com/googleapis/release-please).**
   It does *not* release on every push — it reads the conventional commits since
   the last release and opens (or updates) a **release pull request** containing
   the version bump and the generated changelog.
3. **Merging that release PR** is the only thing that cuts a version: it creates
   the git tag and GitHub Release, bumps `eskoz/__init__.py`, and builds and
   pushes the Docker image to GHCR (`ghcr.io/donasako/eskoz`).

A regular (or even force) push to `main` therefore never changes the version on
its own — only merging the release PR does.

## Documentation

This site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
and deployed to GitHub Pages automatically on every push to `main`. To preview it
locally:

```sh
pip install -r requirements/docs.txt
mkdocs serve
```

Then open <http://127.0.0.1:8000>.
