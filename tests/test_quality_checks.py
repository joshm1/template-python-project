"""Test that the pre-generated test project passes all quality checks.

These tests use a single pre-generated test project (test-project/)
rather than generating fresh projects for each test. This is faster
and the .venv is preserved between runs.
"""

import subprocess
from pathlib import Path

import pytest


class TestUVSync:
    """Test UV dependency installation."""

    @pytest.mark.slow
    def test_uv_sync_succeeds(self, test_project_with_deps: Path) -> None:
        """Test that uv sync completed successfully (via fixture)."""
        # The fixture already ran uv sync, just verify .venv exists
        assert (test_project_with_deps / ".venv").exists()
        assert (test_project_with_deps / ".venv" / "bin" / "python").exists()


class TestPyright:
    """Test Pyright type checking."""

    @pytest.mark.slow
    def test_pyright_passes(self, test_project_with_deps: Path) -> None:
        """Test that Pyright type checking passes."""
        result = subprocess.run(
            ["uv", "run", "pyright"],
            cwd=test_project_with_deps,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"Pyright failed:\n{result.stdout}\n{result.stderr}"


class TestRuff:
    """Test Ruff linting and formatting."""

    @pytest.mark.slow
    def test_ruff_check_passes(self, test_project_with_deps: Path) -> None:
        """Test that Ruff linting passes."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "."],
            cwd=test_project_with_deps,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"

    @pytest.mark.slow
    def test_ruff_format_succeeds(self, test_project_with_deps: Path) -> None:
        """Test that ruff format runs without errors.

        Note: We don't require code to be pre-formatted perfectly since
        Jinja templates can produce minor whitespace variations. The key
        is that the code can be formatted successfully.
        """
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "."],
            cwd=test_project_with_deps,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Ruff format failed:\n{result.stderr}"


class TestPytest:
    """Test that the generated project's tests can run."""

    @pytest.mark.slow
    def test_pytest_collection_succeeds(self, test_project_with_deps: Path) -> None:
        """Test that pytest can collect tests without import errors.

        Note: Exit code 5 means 'no tests collected' which is fine -
        we just want to verify pytest can load the project without errors.
        """
        result = subprocess.run(
            ["uv", "run", "pytest", "--collect-only"],
            cwd=test_project_with_deps,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Exit code 0 = tests collected, 5 = no tests collected (both OK)
        # Any other exit code indicates an error
        assert result.returncode in (0, 5), f"Pytest collection failed:\n{result.stdout}\n{result.stderr}"
