"""Shared pytest fixtures for Copier template testing."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tests.fixtures.copier_configs import TestConfig


# Path to the template root (where copier.yml lives)
TEMPLATE_ROOT = Path(__file__).parent.parent


# =============================================================================
# Git Helper Functions
# =============================================================================


def git_init(path: Path) -> None:
    """Initialize a git repository at the given path."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def git_config(path: Path, email: str = "test@example.com", name: str = "Test User") -> None:
    """Configure git user email and name."""
    subprocess.run(
        ["git", "config", "user.email", email],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", name],
        cwd=path,
        check=True,
        capture_output=True,
    )


def git_add_all(path: Path) -> None:
    """Stage all files in the repository."""
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)


def git_commit(path: Path, message: str) -> None:
    """Create a commit with the given message."""
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=path,
        check=True,
        capture_output=True,
    )


def git_init_and_commit(path: Path, message: str = "Initial commit") -> None:
    """Initialize git repo, configure it, add all files, and commit."""
    git_init(path)
    git_config(path)
    git_add_all(path)
    git_commit(path, message)


def git_reset(path: Path, exclude_patterns: list[str] | None = None) -> None:
    """Reset repository to last commit, optionally excluding patterns from clean."""
    subprocess.run(["git", "checkout", "."], cwd=path, capture_output=True)
    clean_cmd = ["git", "clean", "-fd"]
    for pattern in exclude_patterns or []:
        clean_cmd.extend(["--exclude", pattern])
    subprocess.run(clean_cmd, cwd=path, capture_output=True)


@pytest.fixture(scope="session")
def template_path() -> Path:
    """Return the path to the Copier template root (where copier.yml is)."""
    copier_yml = TEMPLATE_ROOT / "copier.yml"
    assert copier_yml.exists(), f"copier.yml not found at {copier_yml}"
    return TEMPLATE_ROOT


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test output."""
    with tempfile.TemporaryDirectory(prefix="copier_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def generated_project(
    template_path: Path,
    temp_dir: Path,
    request: pytest.FixtureRequest,
) -> Generator[Path, None, None]:
    """Generate a project from the template.

    Use with @pytest.mark.parametrize to test different configurations.

    Example:
        @pytest.mark.parametrize("config", [CLI_SIMPLE, API_POSTGRES])
        def test_generation(generated_project, config):
            assert (generated_project / "pyproject.toml").exists()
    """
    config: TestConfig = request.param
    project_dir = temp_dir / str(config.data["project_slug"])

    # Generate project with Copier
    _run_copier(template_path, project_dir, config.data)

    yield project_dir

    # Cleanup is handled by temp_dir fixture


def _run_copier(
    template_path: Path,
    output_path: Path,
    data: dict[str, str | bool | list[str]],
) -> None:
    """Run Copier to generate a project."""
    import copier

    copier.run_copy(
        str(template_path),
        str(output_path),
        data=data,
        unsafe=True,  # Allow running tasks
        vcs_ref="HEAD",  # Use current HEAD for local templates
        defaults=True,  # Use defaults for unspecified values
    )


@pytest.fixture
def run_in_project(
    generated_project: Path,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Factory fixture to run commands in the generated project directory."""

    def _run(
        cmd: list[str],
        *,
        check: bool = True,
        capture_output: bool = True,
        timeout: int = 120,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command in the generated project directory."""
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        return subprocess.run(
            cmd,
            cwd=generated_project,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            env=full_env,
        )

    return _run


# Pre-generated test project for quality checks
# This is faster than generating a new project for each test
TEST_PROJECT_DIR = TEMPLATE_ROOT / "test-generated-api-sqlite"

# Default test project configuration (API + SQLite exercises most code paths)
TEST_PROJECT_CONFIG = {
    "project_name": "Test Generated API SQLite",
    "project_slug": "test-generated-api-sqlite",
    "package_name": "test_generated_api_sqlite",
    "description": "Pre-generated test project for quality checks",
    "license": "mit",
    "project_type": "api",
    "python_version": "3.13",
    "database_type": "sqlite",
    "_use_alembic_input": True,
    "ruff_strictness": "recommended",
    "dependency_pinning": "flexible",
    "documentation_tier": "standard",
    "git_init": False,
}


def _generate_test_project(force: bool = False) -> Path:
    """Generate the test project if it doesn't exist or force regeneration.

    Preserves .venv if it exists to speed up subsequent runs.
    """
    import copier

    venv_backup = None

    # Backup .venv if it exists
    if TEST_PROJECT_DIR.exists():
        if not force and (TEST_PROJECT_DIR / "pyproject.toml").exists():
            # Project already exists and looks valid
            return TEST_PROJECT_DIR

        venv_path = TEST_PROJECT_DIR / ".venv"
        if venv_path.exists():
            venv_backup = Path(tempfile.mkdtemp()) / ".venv"
            shutil.move(str(venv_path), str(venv_backup))

        # Remove old project (except .venv which we backed up)
        shutil.rmtree(TEST_PROJECT_DIR)

    # Generate fresh project
    copier.run_copy(
        str(TEMPLATE_ROOT),
        str(TEST_PROJECT_DIR),
        data=TEST_PROJECT_CONFIG,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    # Restore .venv if we backed it up
    if venv_backup and venv_backup.exists():
        shutil.move(str(venv_backup), str(TEST_PROJECT_DIR / ".venv"))
        # Clean up backup temp dir
        shutil.rmtree(venv_backup.parent, ignore_errors=True)

    return TEST_PROJECT_DIR


@pytest.fixture(scope="session")
def test_project(template_path: Path) -> Generator[Path, None, None]:
    """Return path to the pre-generated test project.

    This fixture generates the project once per session and preserves
    the .venv directory to speed up subsequent runs.

    The project uses SQLite + API configuration which exercises most
    code paths without requiring external services.
    """
    project_dir = _generate_test_project()
    yield project_dir
    # Don't clean up - we want to preserve .venv for next run


@pytest.fixture(scope="session")
def test_project_with_deps(test_project: Path) -> Path:
    """Return path to test project with dependencies installed.

    This runs `uv sync` once per session.
    """
    # Check if .venv exists and has the right Python
    venv_python = test_project / ".venv" / "bin" / "python"
    if not venv_python.exists():
        subprocess.run(
            ["uv", "sync"],
            cwd=test_project,
            check=True,
            capture_output=True,
            timeout=300,
        )
    return test_project


@pytest.fixture
def test_project_reset(test_project_with_deps: Path) -> Generator[Path, None, None]:
    """Return test project and reset any changes after the test.

    This uses git to track and restore changes, preserving .venv.
    """
    project_dir = test_project_with_deps

    # Initialize git if not already (for tracking changes)
    if not (project_dir / ".git").exists():
        git_init_and_commit(project_dir, "Initial state")

    yield project_dir

    # Reset any changes (preserves .venv since it's gitignored)
    git_reset(project_dir, exclude_patterns=[".venv"])


@pytest.fixture(scope="session")
def docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def devcontainer_cli_available() -> bool:
    """Check if devcontainer CLI is available."""
    try:
        result = subprocess.run(
            ["devcontainer", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
