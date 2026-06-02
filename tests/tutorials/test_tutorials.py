import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from tests.mock_dawaco import build_mock_dawaco_database

REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_NOTEBOOKS_DIR = Path(__file__).resolve().parent
TUTORIALS_DIR = REPO_ROOT / "tutorials"
FAILING_NOTEBOOK_PATH = TEST_NOTEBOOKS_DIR / "failing_notebook.ipynb"
NOTEBOOK_PATHS = tuple(sorted(TUTORIALS_DIR.rglob("*.ipynb")))
FENCED_CODE_BLOCK_RE = re.compile(r"```(?:(?P<language>[A-Za-z0-9_-]+)\n)?(?P<code>.*?)```", re.DOTALL)

SCRIPT_HEADER = """
import builtins
import os

import matplotlib

os.environ["MPLBACKEND"] = "Agg"


def _tutorial_input(*_args, **_kwargs):
    return "4"


def display(*_args, **_kwargs):
    return None


builtins.input = _tutorial_input
matplotlib.use("Agg")
"""


def _sanitise_notebook_source(source: str) -> str:
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("%", "!")):
            continue
        lines.append(line)

    return "\n".join(lines).strip()


def _iter_markdown_code_blocks(source: str):
    for match in FENCED_CODE_BLOCK_RE.finditer(source):
        language = match.group("language")
        if language is not None and language.lower() not in {"py", "python"}:
            continue

        code = match.group("code").strip()
        if code:
            yield code


def _build_tutorial_script(notebook_path: Path) -> str:
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    blocks = [textwrap.dedent(SCRIPT_HEADER).strip()]

    for cell_index, cell in enumerate(notebook["cells"]):
        cell_type = cell["cell_type"]
        source = "".join(cell.get("source", []))
        if cell_type == "code":
            code = _sanitise_notebook_source(source)
            if code:
                blocks.append(f"# %% code cell {cell_index}\n{code}")
        elif cell_type == "markdown":
            for block_index, code in enumerate(_iter_markdown_code_blocks(source)):
                blocks.append(f"# %% markdown cell {cell_index}, block {block_index}\n{code}")

    blocks.append("import matplotlib.pyplot as plt\nplt.close('all')")
    return "\n\n".join(blocks)


def _pythonpath_with_repo_root(env: dict[str, str]) -> str:
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath is None:
        return str(REPO_ROOT)

    return os.pathsep.join([str(REPO_ROOT), existing_pythonpath])


assert NOTEBOOK_PATHS, "No tutorial notebooks found"


def _run_notebook(notebook_path: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    database_path = tmp_path / "mock_dawaco.sqlite"
    engine = build_mock_dawaco_database(database_path)
    engine.dispose()

    script_path = tmp_path / f"{notebook_path.stem}.py"
    script_path.write_text(_build_tutorial_script(notebook_path), encoding="utf-8")

    env = os.environ.copy()
    env["DAWACOTOOLS_DATABASE_URL"] = f"sqlite:///{database_path.resolve().as_posix()}"
    env["DAWACOTOOLS_DB_SCHEMA"] = ""
    env["MPLBACKEND"] = "Agg"
    env["PYTHONPATH"] = _pythonpath_with_repo_root(env)

    return subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=notebook_path.parent,
        env=env,
        timeout=300,
    )


@pytest.mark.parametrize(
    "notebook_path",
    NOTEBOOK_PATHS,
    ids=lambda path: str(path.relative_to(TUTORIALS_DIR)),
)
def test_tutorial_notebook_runs_against_mock_database(notebook_path, tmp_path):
    result = _run_notebook(notebook_path, tmp_path)

    assert result.returncode == 0, (
        f"Tutorial notebook failed: {notebook_path}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_notebook_runner_detects_failing_notebook(tmp_path):
    result = _run_notebook(FAILING_NOTEBOOK_PATH, tmp_path)

    assert result.returncode != 0
    assert "intentional tutorial runner failure" in result.stderr
