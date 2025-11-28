"""Test that Copier generates valid project structures."""

from pathlib import Path

import pytest

from tests.fixtures.copier_configs import ALL_CONFIGS, TestConfig


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_template_generates_successfully(
    template_path: Path,
    temp_dir: Path,
    config: TestConfig,
) -> None:
    """Test that the template generates without errors."""
    import copier

    project_dir = temp_dir / str(config.data["project_slug"])

    # Should not raise any exceptions
    copier.run_copy(
        str(template_path),
        str(project_dir),
        data=config.data,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    assert project_dir.exists()


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_expected_files_exist(
    template_path: Path,
    temp_dir: Path,
    config: TestConfig,
) -> None:
    """Test that expected files are created."""
    import copier

    project_dir = temp_dir / str(config.data["project_slug"])
    copier.run_copy(
        str(template_path),
        str(project_dir),
        data=config.data,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    for expected_file in config.expected_files:
        file_path = project_dir / expected_file
        assert file_path.exists(), f"Expected file missing: {expected_file}"


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_excluded_files_not_present(
    template_path: Path,
    temp_dir: Path,
    config: TestConfig,
) -> None:
    """Test that excluded files are NOT created."""
    import copier

    project_dir = temp_dir / str(config.data["project_slug"])
    copier.run_copy(
        str(template_path),
        str(project_dir),
        data=config.data,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    for excluded_file in config.excluded_files:
        file_path = project_dir / excluded_file
        assert not file_path.exists(), f"Excluded file should not exist: {excluded_file}"


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_pyproject_is_valid_toml(
    template_path: Path,
    temp_dir: Path,
    config: TestConfig,
) -> None:
    """Test that pyproject.toml is valid TOML."""
    import copier
    import tomllib

    project_dir = temp_dir / str(config.data["project_slug"])
    copier.run_copy(
        str(template_path),
        str(project_dir),
        data=config.data,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    pyproject_path = project_dir / "pyproject.toml"
    assert pyproject_path.exists()

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Verify basic structure
    assert "project" in data
    assert "name" in data["project"]
    assert data["project"]["name"] == config.data["project_slug"]


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_no_unrendered_jinja_templates(
    template_path: Path,
    temp_dir: Path,
    config: TestConfig,
) -> None:
    """Test that no Jinja2 template syntax remains in generated files."""
    import copier

    project_dir = temp_dir / str(config.data["project_slug"])
    copier.run_copy(
        str(template_path),
        str(project_dir),
        data=config.data,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    # Patterns that indicate unrendered Jinja2
    jinja_patterns = [
        "{{ ",
        " }}",
        "{% ",
        " %}",
        "{# ",
        " #}",
    ]

    # Files that legitimately use Jinja-like syntax
    skip_files = {"CLAUDE.md", "justfile"}  # justfile uses its own {% if os() %} syntax

    for file_path in project_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix not in {".pyc", ".pyo"}:
            if file_path.name in skip_files:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                for pattern in jinja_patterns:
                    if pattern in content:
                        pytest.fail(
                            f"Unrendered Jinja2 found in {file_path.relative_to(project_dir)}: {pattern}"
                        )
            except UnicodeDecodeError:
                pass  # Skip binary files
