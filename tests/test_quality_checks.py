"""Test that generated projects pass all quality checks."""

from pathlib import Path

import pytest

from tests.fixtures.copier_configs import ALL_CONFIGS, TestConfig


class TestUVSync:
    """Test UV dependency installation."""

    @pytest.mark.slow
    @pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
    def test_uv_sync_succeeds(
        self,
        template_path: Path,
        temp_dir: Path,
        config: TestConfig,
    ) -> None:
        """Test that uv sync completes successfully."""
        import copier
        import subprocess

        project_dir = temp_dir / str(config.data["project_slug"])
        copier.run_copy(
            str(template_path),
            str(project_dir),
            data=config.data,
            unsafe=True,
            vcs_ref="HEAD",
            defaults=True,
        )

        result = subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for slow networks
        )

        assert result.returncode == 0, f"uv sync failed:\n{result.stderr}"

        # Verify .venv was created
        assert (project_dir / ".venv").exists()


class TestPyright:
    """Test Pyright type checking."""

    @pytest.mark.slow
    @pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
    def test_pyright_passes(
        self,
        template_path: Path,
        temp_dir: Path,
        config: TestConfig,
    ) -> None:
        """Test that Pyright type checking passes."""
        import copier
        import subprocess

        project_dir = temp_dir / str(config.data["project_slug"])
        copier.run_copy(
            str(template_path),
            str(project_dir),
            data=config.data,
            unsafe=True,
            vcs_ref="HEAD",
            defaults=True,
        )

        # Install dependencies first
        subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            timeout=300,
        )

        # Run Pyright
        result = subprocess.run(
            ["uv", "run", "pyright"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"Pyright failed:\n{result.stdout}\n{result.stderr}"


class TestRuff:
    """Test Ruff linting and formatting."""

    @pytest.mark.slow
    @pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
    def test_ruff_check_passes(
        self,
        template_path: Path,
        temp_dir: Path,
        config: TestConfig,
    ) -> None:
        """Test that Ruff linting passes."""
        import copier
        import subprocess

        project_dir = temp_dir / str(config.data["project_slug"])
        copier.run_copy(
            str(template_path),
            str(project_dir),
            data=config.data,
            unsafe=True,
            vcs_ref="HEAD",
            defaults=True,
        )

        # Install dependencies first
        subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            timeout=300,
        )

        # Run Ruff check
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "."],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"

    @pytest.mark.slow
    @pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
    def test_ruff_format_check(
        self,
        template_path: Path,
        temp_dir: Path,
        config: TestConfig,
    ) -> None:
        """Test that code is already formatted correctly."""
        import copier
        import subprocess

        project_dir = temp_dir / str(config.data["project_slug"])
        copier.run_copy(
            str(template_path),
            str(project_dir),
            data=config.data,
            unsafe=True,
            vcs_ref="HEAD",
            defaults=True,
        )

        # Install dependencies first
        subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            timeout=300,
        )

        # Check formatting (--check mode)
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "."],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"
