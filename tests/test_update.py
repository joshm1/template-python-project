"""Test that copier update works correctly when template changes.

These tests use a pre-generated project approach similar to test_quality_checks.py,
but require creating a git-tracked template since copier update needs git refs.
"""

import shutil
import subprocess
from pathlib import Path

import copier
import pytest
import yaml

from tests.conftest import TEMPLATE_ROOT

# Configuration for update test project (simpler than API project for speed)
UPDATE_TEST_CONFIG = {
    "project_name": "Update Test CLI",
    "project_slug": "update-test-cli",
    "package_name": "update_test_cli",
    "description": "Test project for copier update functionality",
    "license": "mit",
    "project_type": "cli",
    "python_version": "3.13",
    "database_type": "none",
    "ruff_strictness": "minimal",
    "dependency_pinning": "flexible",
    "documentation_tier": "minimal",
    "git_init": False,  # We'll handle git ourselves
}


@pytest.fixture(scope="module")
def git_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a copy of the template as a git repository.

    Copier requires the template to be a git repository for update functionality.
    This fixture copies the template to a temp dir and initializes it as a git repo.

    Scope is 'module' to reuse across all tests in this file.
    """
    template_copy = tmp_path_factory.mktemp("template") / "template-git"
    shutil.copytree(TEMPLATE_ROOT, template_copy)

    # Initialize git in the template copy
    subprocess.run(["git", "init"], cwd=template_copy, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=template_copy,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=template_copy,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=template_copy, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial template commit"],
        cwd=template_copy,
        check=True,
        capture_output=True,
    )

    return template_copy


@pytest.fixture(scope="module")
def update_test_project(
    git_template: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Generate a project from the git template for update testing.

    This project is reused across tests in this module.
    """
    project_dir = tmp_path_factory.mktemp("projects") / "update-test-cli"

    # Generate project from git template
    copier.run_copy(
        str(git_template),
        str(project_dir),
        data=UPDATE_TEST_CONFIG,
        unsafe=True,
        vcs_ref="HEAD",
        defaults=True,
    )

    # Initialize git in generated project (required for copier update)
    subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit from template"],
        cwd=project_dir,
        check=True,
        capture_output=True,
    )

    return project_dir


@pytest.fixture
def clean_update_project(update_test_project: Path) -> Path:
    """Return the update test project and reset changes after each test."""
    yield update_test_project

    # Reset any changes made during test
    subprocess.run(
        ["git", "checkout", "."],
        cwd=update_test_project,
        capture_output=True,
    )
    subprocess.run(
        ["git", "clean", "-fd"],
        cwd=update_test_project,
        capture_output=True,
    )


class TestCopierUpdate:
    """Test copier update functionality."""

    @pytest.mark.slow
    def test_update_succeeds_without_changes(
        self,
        clean_update_project: Path,
    ) -> None:
        """Test that copier update runs without errors on unchanged template."""
        # Run copier update - should succeed without errors
        copier.run_update(
            str(clean_update_project),
            unsafe=True,
            defaults=True,
            overwrite=True,
        )

        # Verify project still valid
        assert (clean_update_project / "pyproject.toml").exists()
        assert (clean_update_project / "src").exists()
        assert (clean_update_project / "src" / "update_test_cli").exists()

    @pytest.mark.slow
    def test_update_preserves_user_files(
        self,
        clean_update_project: Path,
    ) -> None:
        """Test that user-added files (not from template) are preserved."""
        # Add a user file (not from template)
        user_file = clean_update_project / "src" / "update_test_cli" / "custom_module.py"
        user_file.write_text('"""Custom user module."""\n\nUSER_CONSTANT = 42\n')

        subprocess.run(
            ["git", "add", "."],
            cwd=clean_update_project,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add custom module"],
            cwd=clean_update_project,
            check=True,
            capture_output=True,
        )

        # Run copier update
        copier.run_update(
            str(clean_update_project),
            unsafe=True,
            defaults=True,
            overwrite=True,
        )

        # Verify user file is preserved
        assert user_file.exists(), "User file should be preserved after update"
        content = user_file.read_text()
        assert "USER_CONSTANT = 42" in content

    @pytest.mark.slow
    def test_update_restores_template_files(
        self,
        clean_update_project: Path,
    ) -> None:
        """Test that template changes overwrite local modifications when overwrite=True."""
        # Modify a template-generated file
        readme = clean_update_project / "README.md"
        original_content = readme.read_text()
        readme.write_text("# Modified by user\n\nThis was changed.\n")

        subprocess.run(
            ["git", "add", "."],
            cwd=clean_update_project,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Modify README"],
            cwd=clean_update_project,
            check=True,
            capture_output=True,
        )

        # Run copier update with overwrite
        copier.run_update(
            str(clean_update_project),
            unsafe=True,
            defaults=True,
            overwrite=True,
        )

        # With overwrite=True, template version should be restored
        updated_content = readme.read_text()
        # The content should match the template output (project name in title)
        assert "Update Test CLI" in updated_content or "update-test-cli" in updated_content

    @pytest.mark.slow
    def test_answers_file_valid(
        self,
        clean_update_project: Path,
    ) -> None:
        """Test that .copier-answers.yml contains valid data."""
        answers_file = clean_update_project / ".copier-answers.yml"
        assert answers_file.exists(), ".copier-answers.yml should exist"

        with open(answers_file) as f:
            answers = yaml.safe_load(f)

        assert answers is not None
        assert answers.get("project_name") == UPDATE_TEST_CONFIG["project_name"]
        assert answers.get("project_slug") == UPDATE_TEST_CONFIG["project_slug"]
        # Copier metadata should be present
        assert "_commit" in answers or "_src_path" in answers
