"""Test that copier update works correctly.

These tests use the pre-generated test project (test-generated-api-sqlite)
which must be regenerated when template changes to keep _commit in sync.
"""

import subprocess
from pathlib import Path

import copier
import pytest
import yaml

from tests.conftest import (
    TEST_PROJECT_CONFIG,
    git_add_all,
    git_commit,
    git_init_and_commit,
    git_reset,
)


def _ensure_clean_git(project_dir: Path) -> None:
    """Ensure project has git initialized and is in a clean state."""
    if not (project_dir / ".git").exists():
        git_init_and_commit(project_dir, "Initial commit")
    else:
        # Reset any dirty state from previous tests
        git_reset(project_dir, exclude_patterns=[".venv"])
        # Commit any untracked changes (like restored files from reset)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            git_add_all(project_dir)
            git_commit(project_dir, "Reset to clean state")


class TestCopierUpdate:
    """Test copier update functionality."""

    @pytest.mark.slow
    def test_update_succeeds_without_changes(
        self,
        test_project_with_deps: Path,
    ) -> None:
        """Test that copier update runs without errors on unchanged template."""
        project_dir = test_project_with_deps

        _ensure_clean_git(project_dir)

        # Run copier update - should succeed without errors
        copier.run_update(
            str(project_dir),
            unsafe=True,
            defaults=True,
            overwrite=True,
        )

        # Verify project still valid
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "src").exists()

    @pytest.mark.slow
    def test_update_preserves_user_files(
        self,
        test_project_with_deps: Path,
    ) -> None:
        """Test that user-added files (not from template) are preserved."""
        project_dir = test_project_with_deps
        # Derive package_name from project_name (same as copier does)
        package_name = TEST_PROJECT_CONFIG["project_name"].lower().replace(" ", "_").replace("-", "_")

        _ensure_clean_git(project_dir)

        # Add a user file (not from template) with unique content
        user_file = project_dir / "src" / package_name / "custom_module.py"
        import time

        unique_value = int(time.time())
        user_file.write_text(f'"""Custom user module."""\n\nUSER_CONSTANT = {unique_value}\n')

        git_add_all(project_dir)
        git_commit(project_dir, "Add custom module")

        # Run copier update
        copier.run_update(
            str(project_dir),
            unsafe=True,
            defaults=True,
            overwrite=True,
        )

        # Verify user file is preserved
        assert user_file.exists(), "User file should be preserved after update"
        content = user_file.read_text()
        assert f"USER_CONSTANT = {unique_value}" in content

        # Cleanup: remove user file and commit
        user_file.unlink()
        git_add_all(project_dir)
        git_commit(project_dir, "Remove custom module")

    @pytest.mark.slow
    def test_answers_file_valid(
        self,
        test_project_with_deps: Path,
    ) -> None:
        """Test that .copier-answers.yml contains valid data."""
        answers_file = test_project_with_deps / ".copier-answers.yml"
        assert answers_file.exists(), ".copier-answers.yml should exist"

        with open(answers_file) as f:
            answers = yaml.safe_load(f)

        assert answers is not None
        assert answers.get("project_name") == TEST_PROJECT_CONFIG["project_name"]
        # project_slug is derived from project_name
        expected_slug = TEST_PROJECT_CONFIG["project_name"].lower().replace(" ", "-").replace("_", "-")
        assert answers.get("project_slug") == expected_slug
        # Copier metadata should be present
        assert "_commit" in answers, "Should have _commit for update tracking"
        assert "_src_path" in answers, "Should have _src_path for template location"

    @pytest.mark.slow
    def test_answers_commit_is_valid(
        self,
        test_project_with_deps: Path,
        template_path: Path,
    ) -> None:
        """Test that _commit in answers file references a valid git commit."""
        answers_file = test_project_with_deps / ".copier-answers.yml"

        with open(answers_file) as f:
            answers = yaml.safe_load(f)

        commit_hash = answers.get("_commit")
        assert commit_hash, "Should have _commit value"

        # Verify commit exists in template repo
        result = subprocess.run(
            ["git", "cat-file", "-t", commit_hash],
            cwd=template_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Commit {commit_hash} should exist in template repo"
        assert result.stdout.strip() == "commit", f"{commit_hash} should be a commit object"
