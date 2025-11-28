"""Copier template extensions for git config defaults."""

import subprocess

from copier_templates_extensions import ContextUpdater


class GitConfigContext(ContextUpdater):
    """Provides git config user.name and user.email as template context."""

    def update_context(self, context: dict) -> dict:
        """Add git config values to the template context."""
        context["git_user_name"] = self._get_git_config("user.name")
        context["git_user_email"] = self._get_git_config("user.email")
        return context

    def _get_git_config(self, key: str) -> str:
        """Get a git config value, returning empty string on failure."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", key],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
