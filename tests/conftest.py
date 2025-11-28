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


# Path to the template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "template"


@pytest.fixture(scope="session")
def template_path() -> Path:
    """Return the path to the Copier template."""
    assert TEMPLATE_DIR.exists(), f"Template not found at {TEMPLATE_DIR}"
    return TEMPLATE_DIR


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
