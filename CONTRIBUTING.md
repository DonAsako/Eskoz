# Contributing to Eskoz

First off, thank you for considering contributing! Eskoz is an open-source project, and contributions, big or small, are always welcome.

## Ways to Contribute

You can help in many ways, including:

- Code patches and new features  
- Bug reports and troubleshooting  
- Documentation improvements  
- Reviewing pull requests  

Starring the repository is appreciated!

## Getting Started

1. **Fork the repository** and clone it locally:

```bash
git clone git@github.com:DonAsako/Eskoz.git
cd Eskoz
```

2. **Set up your environment** (see [README.md](https://github.com/DonAsako/Eskoz#deploy-with-docker) for Docker or local setup instructions).  

3. **Create a new branch** for your changes.  

4. **Submit a pull request** with a clear description of your changes.  
   - For non-trivial changes, please open an [issue](https://github.com/DonAsako/Eskoz/issues) first and reference it in your PR.

## Commit Convention

Eskoz uses [Conventional Commits](https://www.conventionalcommits.org/). The commit
message **prefix drives automated versioning and the changelog**, so it matters:

| Prefix      | Meaning                          | Version bump |
| ----------- | -------------------------------- | ------------ |
| `feat:`     | A new feature                    | minor        |
| `fix:`      | A bug fix                        | patch        |
| `perf:`     | A performance improvement        | patch        |
| `refactor:` | Code change, no behaviour change | patch        |
| `docs:`     | Documentation only               | none         |
| `chore:`    | Tooling, deps, housekeeping      | none         |

A breaking change is marked with `!` (e.g. `feat!: ...`) or a `BREAKING CHANGE:`
footer, and triggers a **major** bump.

```
feat(blog): add scheduled publishing
fix(admin): handle anonymous user on the dashboard
```

Commit messages are linted by `gitlint` (via a `commit-msg` hook), so a malformed
message is rejected before it lands.

## Local Quality Checks

Quality is enforced by [pre-commit](https://pre-commit.com/). Install the hooks once,
then they run automatically on every commit:

```bash
pip install -r requirements/development.txt
pre-commit install            # installs both pre-commit and commit-msg hooks
pre-commit run --all-files    # run everything on demand
```

The hooks cover Ruff (lint + format), djLint, yamllint, gitleaks (secret scanning),
gitlint, and `manage.py check` / migration checks.

## Running Tests

Tests are plain Django `TestCase`s under each app's `tests.py`. Locally they run on
SQLite via the development settings:

```bash
export DJANGO_SETTINGS_MODULE=eskoz.settings.development
export DJANGO_SECRET_KEY=dev-dummy-key
python manage.py test apps.analytics apps.blog apps.core apps.education apps.infosec -t .
```

> The `-t .` flag sets the test discovery top-level directory to the repo root so the
> `apps.*.models` packages import under their real dotted path.

In CI, the same suite runs against **PostgreSQL** using `eskoz.settings.ci`, to match
production.

## Continuous Integration & Releases

Everything from a merge to a published release is automated:

1. **On every pull request and push to `main`**, the `CI` workflow runs:
   - **quality** — the full pre-commit suite;
   - **tests** — the Django test suite against PostgreSQL.

2. **Versioning is handled by [release-please](https://github.com/googleapis/release-please).**
   It does **not** release on every push. Instead, it reads the conventional commits
   since the last release and opens (or updates) a **release pull request** containing
   the version bump and the generated `CHANGELOG.md` entry.

3. **Merging that release PR** is the only thing that cuts a version. It creates the
   git tag, the GitHub Release, bumps `eskoz/__init__.py`, and **builds and pushes the
   Docker image to GHCR** (`ghcr.io/donasako/eskoz`, tagged `latest`, `vX.Y.Z`, `X.Y`).

A regular (or even force) push to `main` therefore never changes the version on its own
— only merging the release PR does.

## Code of Conduct

Please see our [Code of Conduct](.github/CODE_OF_CONDUCT.md) for guidelines on participating in the Eskoz community. By contributing, you agree to follow these rules to help maintain a welcoming and productive environment.
