# python-dawaco-tools

Tools to read the Dawaco database written in Python. Have a look at the tutorials folder to get started.

# Installation instructions

## Install ODBC driver

We need a ODBC driver to create the connection with the SQL database.

Download version 18 for x64 platform of the ODBC driver from the microsoft website. https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

## Setup workflow with project files on OneDrive (PWN)

Here we start a workflow with project files or personal scripts on OneDrive. The Python environment is installed to `C:\PythonScripts\Environments\dawacotools\`.

### Clone the dawacotools github-repository

## Install environment PWN employees

- Use GitHub Desktop to clone github.com/bdestombe/python-dawaco-tools to this exact local directory: "C:\PythonScripts\Repositories\bdestombe\python-dawaco-tools"
-
- VSCode > Open Folder: project folder > Command prompt
  - Create `C:\PythonScripts\Environments\dawacotools` folder
  - `uv venv --python=3.13 --directory=C:\PythonScripts\Environments\dawacotools`
  - `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\activate`
  - `uv pip install -e "C:\PythonScripts\Repositories\bdestombe\python-dawaco-tools"`
  - <kbd> <br> Ctrl <br> </kbd> + <kbd> <br> Shift <br> </kbd> + <kbd> <br> P <br> </kbd> => "Python: Select Interpreter" => "Enter interpreter path..." => `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\python.exe`

The environment is now installed in `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\python.exe`

## Development

Install the package with development tools:

```powershell
$env:UV_PROJECT_ENVIRONMENT = ".venv-claude"
uv sync --extra test
```

Markdown/YAML formatting uses Prettier through `npx`; install Node.js/npm before running the Prettier command below.
The pinned Prettier version keeps local checks aligned with CI.

Run the CI-safe test suite against the synthetic SQLite DAWACO database:

```powershell
uv run pytest tests
```

The CI workflow does not execute tutorial notebooks; validate tutorial changes manually.

Run a single test:

```powershell
uv run pytest tests\test_io.py::test_get_daw_filters_supports_filter_and_expired_selection -n0
```

Run linting and formatting checks:

```powershell
uv run ruff format --diff dawacotools tests
uv run ruff check dawacotools tests
uv run ty check dawacotools tests --ignore unused-ignore-comment
uv run validate-pyproject pyproject.toml
npx --yes prettier@3.8.3 --check "**/*.{yaml,yml,md}"
```

Ruff and ty run over the package and tests. `ruff.toml` keeps a small explicit legacy baseline for public API boolean parameters, assertions, docstrings, dynamic table names, and domain constants; remove entries from that baseline as modules are modernized.

The default tests build a fully synthetic SQLite database in pytest's temporary directory. These rows are fabricated and safe for CI. Do not commit exports or samples from the production DAWACO database. Local database and geospatial export files are ignored so private mock databases generated from production data stay out of git.

To create the same fabricated CI database as a persistent local SQLite file:

```powershell
uv run python -m tests.mock_dawaco .\scratch\ci_mock_dawaco.sqlite
```

Private local mock databases can be used for opt-in smoke tests by pointing SQLAlchemy at a local database URL:

```powershell
$env:DAWACOTOOLS_PRIVATE_DATABASE_URL = "sqlite:///C:\path\to\private_mock.sqlite"
uv run pytest tests --run-private-db -m private_db -n0
```

The CI test database in `tests\mock_dawaco.py` must remain fully synthetic. If you generate richer private mock data from the original database, keep it outside the repository and do not copy values back into tests or documentation. Private tests must assert only schema, shape, and physical/data-quality invariants; they must not encode original DAWACO values.

## DAWACO database configuration

By default, DAWACO SQL Server access uses ODBC Driver 18, database `Dawacoprod`, schema `dbo`, and `Authentication=ActiveDirectoryInteractive`. Users can override the Azure AD authentication mode without editing package code:

```powershell
$env:DAWACOTOOLS_ODBC_AUTHENTICATION = "ActiveDirectoryIntegrated"
```

To replace the complete ODBC connection string, set:

```powershell
$env:DAWACOTOOLS_CONNECTION_STRING = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=...;PORT=1433;DATABASE=...;Authentication=ActiveDirectoryInteractive;"
```

To run local live smoke tests against the real DAWACO database:

```powershell
$env:DAWACOTOOLS_LIVE_MPCODE = "..."
$env:DAWACOTOOLS_LIVE_FILTER = "1"
uv run pytest tests --run-live-db -m live_db -n0
```
