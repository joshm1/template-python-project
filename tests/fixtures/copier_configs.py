"""Test configuration matrix for Copier template testing.

Each configuration represents a realistic project setup that users might generate.
"""

from dataclasses import dataclass, field


@dataclass
class TestConfig:
    """Configuration for a single template test case."""

    name: str
    """Human-readable test name for identification."""

    data: dict[str, str | bool | list[str]]
    """Copier data values to pass during generation."""

    expected_files: list[str] = field(default_factory=list)
    """Files that MUST exist after generation."""

    excluded_files: list[str] = field(default_factory=list)
    """Files that MUST NOT exist after generation."""

    skip_docker: bool = False
    """Skip Docker-related tests for this config."""

    skip_server: bool = False
    """Skip server startup tests (e.g., for CLI/library projects)."""


# =============================================================================
# NOTE: Docker and DevContainers are ALWAYS included in all projects.
# The use_docker and use_devcontainer variables have been removed from
# the template configuration. All test configs should expect Docker and
# DevContainer files to be present.
# =============================================================================

# =============================================================================
# CLI Tool Configurations
# =============================================================================

CLI_SIMPLE = TestConfig(
    name="cli_simple",
    data={
        "project_name": "Test CLI Tool",
        "project_slug": "test-cli-tool",
        "package_name": "test_cli_tool",
        "description": "A simple CLI tool for testing",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "project_type": "cli",
        "python_version": "3.13",
        "database_type": "none",
        "ruff_strictness": "recommended",
        "dependency_pinning": "flexible",
        "documentation_tier": "standard",
        "git_init": False,
    },
    expected_files=[
        "pyproject.toml",
        "justfile",
        "CLAUDE.md",
        "README.md",
        "src/test_cli_tool/__init__.py",
        "src/test_cli_tool/cli.py",
        "src/test_cli_tool/py.typed",
        "tests/conftest.py",
        ".devcontainer/devcontainer.json",
        ".pre-commit-config.yaml",
        "docker-compose.yml",
        "Dockerfile",
    ],
    excluded_files=[
        "alembic.ini",
        "src/test_cli_tool/main.py",  # FastAPI main
    ],
    skip_server=True,
)

CLI_WITH_SQLITE = TestConfig(
    name="cli_with_sqlite",
    data={
        "project_name": "CLI with Database",
        "project_slug": "cli-with-db",
        "package_name": "cli_with_db",
        "description": "CLI tool with SQLite database",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "project_type": "cli",
        "python_version": "3.13",
        "database_type": "sqlite",
        "ruff_strictness": "recommended",
        "dependency_pinning": "flexible",
        "documentation_tier": "standard",
        "git_init": False,
    },
    expected_files=[
        "src/cli_with_db/core/database.py",
        ".devcontainer/devcontainer.json",
        "docker-compose.yml",
    ],
    skip_server=True,
)

# =============================================================================
# API Service Configurations
# =============================================================================

API_POSTGRES = TestConfig(
    name="api_postgres",
    data={
        "project_name": "API with PostgreSQL",
        "project_slug": "api-postgres",
        "package_name": "api_postgres",
        "description": "FastAPI service with PostgreSQL",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "project_type": "api",
        "python_version": "3.13",
        "database_type": "postgresql",
        "use_alembic": True,
        "ruff_strictness": "recommended",
        "dependency_pinning": "flexible",
        "documentation_tier": "standard",
        "git_init": False,
    },
    expected_files=[
        "pyproject.toml",
        "docker-compose.yml",
        "Dockerfile",
        ".dockerignore",
        "alembic.ini",
        "alembic/env.py",
        "src/api_postgres/main.py",
        "src/api_postgres/core/database.py",
        "src/api_postgres/core/config.py",
        ".devcontainer/devcontainer.json",
        ".devcontainer/Dockerfile",
        ".devcontainer/docker-compose.yml",
    ],
)

API_MINIMAL = TestConfig(
    name="api_minimal",
    data={
        "project_name": "Minimal API",
        "project_slug": "minimal-api",
        "package_name": "minimal_api",
        "description": "Minimal FastAPI service",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "project_type": "api",
        "python_version": "3.13",
        "database_type": "none",
        "ruff_strictness": "minimal",
        "dependency_pinning": "flexible",
        "documentation_tier": "minimal",
        "git_init": False,
    },
    expected_files=[
        "src/minimal_api/main.py",
        "docker-compose.yml",
        ".devcontainer/devcontainer.json",
    ],
    excluded_files=[
        "alembic.ini",  # no database
    ],
)

# =============================================================================
# Library Configurations
# =============================================================================

LIBRARY_SIMPLE = TestConfig(
    name="library_simple",
    data={
        "project_name": "My Library",
        "project_slug": "my-library",
        "package_name": "my_library",
        "description": "A reusable Python library",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "project_type": "library",
        "python_version": "3.13",
        "ruff_strictness": "recommended",
        "dependency_pinning": "flexible",
        "documentation_tier": "standard",
        "git_init": False,
    },
    expected_files=[
        "src/my_library/__init__.py",
        "src/my_library/py.typed",
        "docs/README.md",
        "docker-compose.yml",
        ".devcontainer/devcontainer.json",
    ],
    excluded_files=[
        "src/my_library/cli.py",
        "src/my_library/main.py",
    ],
    skip_server=True,
)

# =============================================================================
# All Configurations for Parametrized Tests
# =============================================================================

ALL_CONFIGS: list[TestConfig] = [
    CLI_SIMPLE,
    CLI_WITH_SQLITE,
    API_POSTGRES,
    API_MINIMAL,
    LIBRARY_SIMPLE,
]

# Quick smoke test subset (fast CI)
SMOKE_CONFIGS: list[TestConfig] = [
    CLI_SIMPLE,
    API_POSTGRES,
    LIBRARY_SIMPLE,
]

# Configs that require Docker
DOCKER_CONFIGS: list[TestConfig] = [
    config for config in ALL_CONFIGS if not config.skip_docker
]

# Configs with FastAPI servers
SERVER_CONFIGS: list[TestConfig] = [
    config for config in ALL_CONFIGS if not config.skip_server
]
