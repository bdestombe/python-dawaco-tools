# python-dawaco-tools

Python tools for reading and analysing DAWACO groundwater monitoring data.

## Repository layout

- `dawacotools\` -- importable package code.
- `tests\` -- pytest suite, including the synthetic SQLite DAWACO database builder in `tests\mock_dawaco.py`.
- `workflows\` -- project-specific scripts and notebooks/workflows. Treat these as data workflows, not package tests.
- `.github\workflows\` -- CI for Windows functional tests, linting, type checking, metadata validation, and Prettier.
- `tutorials\` -- user-facing examples.

## Development commands

Use a task-local uv environment rather than a user's active virtual environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT = ".venv-claude"
uv sync --extra test -q
```

Run the default CI-safe tests against the synthetic DAWACO database:

```powershell
uv run pytest tests
```

Run the configured Python checks:

```powershell
uv run ruff format --diff dawacotools tests
uv run ruff check tests dawacotools\__init__.py
uv run ty check tests --ignore unused-ignore-comment
uv run validate-pyproject pyproject.toml
```

Markdown and YAML formatting is checked with a pinned Prettier version through `npx`; Node.js/npm must be
available:

```powershell
npx --yes prettier@3.8.3 --check "**/*.{yaml,yml,md}"
```

CI also verifies the lowest direct test dependencies on Python 3.12:

```powershell
uv sync --extra test --resolution lowest-direct --python 3.12
uv run pytest tests -n0
```

## DAWACO database handling

- Default tests must use the fully synthetic SQLite database created by `tests\mock_dawaco.py`.
- Synthetic test data may be committed only when it is fabricated and safe for public CI.
- Private mock databases may be used only through `DAWACOTOOLS_PRIVATE_DATABASE_URL` or
  `DAWACOTOOLS_DATABASE_URL` plus `uv run pytest tests --run-private-db -m private_db -n0`.
- Live DAWACO smoke tests require explicit opt-in with `--run-live-db` or `DAWACOTOOLS_RUN_LIVE_DB=1` and local
  credentials/environment such as `DAWACOTOOLS_LIVE_MPCODE` and `DAWACOTOOLS_LIVE_FILTER`.
- Never run private or live database tests in CI unless a workflow is explicitly designed for protected secrets.

## Data safety

- Do not commit production DAWACO exports, private mock databases, connection strings, credentials, tokens, or
  identifiable monitoring values copied from production.
- Keep generated `.db`, `.sqlite`, `.sqlite3`, `.sql`, `.gpkg`, `.geojson`, `.feather`, `.parquet`, images, and
  archives out of git; `.gitignore` is configured for these data/export formats.
- Tests for private data must assert schema, shape, and data-quality invariants only; do not encode real DAWACO
  values in tests, docs, or examples.
- Be careful with `workflows\` scripts: many are local/project analyses and may read or produce private data.

## Coding guidance

- Keep changes scoped. Do not perform broad package lint, type, or API cleanup unless it is required for the task.
- Prefer small, well-named tests in `tests\` for package behavior changes.
- Public APIs should have type hints and clear docstrings, but avoid reshaping unrelated legacy code.
- Re-read the request before finishing and run the relevant configured checks.
