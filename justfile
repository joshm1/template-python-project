# Justfile for managing the Python project template
# https://github.com/casey/just

# Show available recipes
default:
    @just --list

# =============================================================================
# Setup & Dependencies
# =============================================================================

# Install dependencies (run this first)
install:
    uv sync

# Update dependencies to latest versions
update:
    uv lock --upgrade && uv sync

# Full setup: install deps + verify everything works
setup: install
    @echo "Verifying template..."
    @just validate
    @echo "Setup complete! Run 'just test-template-fast' to run tests."

# =============================================================================
# Project Generation
# =============================================================================

# Generate a new project interactively
generate destination:
    uv run copier copy --trust . "{{destination}}"

# Generate a new project with dirty changes (useful during template development)
generate-dev destination:
    uv run copier copy --trust --vcs-ref HEAD . "{{destination}}"

# Generate a project with all defaults (non-interactive, for testing)
generate-defaults destination name="test-project":
    uv run copier copy --trust --force --defaults -d "project_name={{name}}" . "{{destination}}"

# Generate a project with specific options (non-interactive)
generate-with destination name="my-project" type="cli" +DATA="":
    uv run copier copy --trust --force -d "project_name={{name}}" -d "project_type={{type}}" {{DATA}} . "{{destination}}"

# Update an existing project generated from this template
update-project destination:
    uv run copier update --trust "{{destination}}"

# Update project with dirty changes (useful during template development)
update-project-dev destination:
    uv run copier update --trust --vcs-ref HEAD "{{destination}}"

# Validate the template by generating a test project
validate:
    #!/usr/bin/env bash
    set -euo pipefail
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    echo "Generating test project in $TEMP_DIR..."
    uv run copier copy --trust --force --defaults -d "project_name=Template Test" --vcs-ref HEAD . "$TEMP_DIR"
    echo "Template generated successfully!"
    ls -la "$TEMP_DIR"

# Show template questions/configuration
show-config:
    @cat copier.yml

# =============================================================================
# Template Testing (Meta-Testing)
# =============================================================================

# Run all template tests
test-template:
    uv run pytest tests/ -v

# Run only fast tests (no Docker, no slow tests)
test-template-fast:
    uv run pytest tests/ -v -m "not slow and not docker and not devcontainer"

# Run smoke tests (minimal subset)
test-template-smoke:
    uv run pytest tests/test_generation.py -v -k "cli_simple or api_postgres or library_simple"

# Run generation tests only
test-generation:
    uv run pytest tests/test_generation.py -v

# Run quality check tests only
test-quality:
    uv run pytest tests/test_quality_checks.py -v

# Run Docker tests only (requires Docker)
test-docker:
    uv run pytest tests/test_docker.py -v -m docker

# Run devcontainer tests only (requires devcontainer CLI)
test-devcontainer:
    uv run pytest tests/test_devcontainer.py -v -m devcontainer

# Run FastAPI server tests
test-server:
    uv run pytest tests/test_fastapi.py -v

# Run tests in parallel (faster but needs more resources)
test-template-parallel:
    uv run pytest tests/ -v -n auto

# Run tests with coverage report
test-template-coverage:
    uv run pytest tests/ --cov=template --cov-report=term-missing --cov-report=html

# Type check the test files
typecheck-tests:
    uv run pyright tests/

# Lint test files
lint-tests:
    uv run ruff check tests/

# Format test files
format-tests:
    uv run ruff format tests/

# Clean up test artifacts
clean-test:
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete

# =============================================================================
# Pre-generated Test Project
# =============================================================================

# Generate/regenerate the test project (test-generated-api-sqlite)
test-project-generate:
    #!/usr/bin/env bash
    set -euo pipefail

    PROJECT_DIR="test-generated-api-sqlite"

    # Backup .venv if it exists
    if [ -d "$PROJECT_DIR/.venv" ]; then
        echo "Backing up .venv..."
        mv "$PROJECT_DIR/.venv" "/tmp/test-project-venv-backup"
    fi

    # Remove old project
    rm -rf "$PROJECT_DIR"

    # Generate fresh project (minimal config, let copier derive the rest)
    echo "Generating test project..."
    uv run copier copy --trust --force --defaults --vcs-ref HEAD \
        -d "project_name=Test Generated API SQLite" \
        -d "project_type=api" \
        -d "database_type=sqlite" \
        -d "git_init=false" \
        . "$PROJECT_DIR"

    # Restore .venv if we backed it up
    if [ -d "/tmp/test-project-venv-backup" ]; then
        echo "Restoring .venv..."
        mv "/tmp/test-project-venv-backup" "$PROJECT_DIR/.venv"
    fi

    echo "Test project regenerated at $PROJECT_DIR"
    echo ""
    echo "To verify, run: just test-quality"

# Install deps in test project and run quality checks
test-project-quality:
    cd test-generated-api-sqlite && uv sync && uv run pyright && uv run ruff check . && uv run ruff format --check .

# Run copier update on test project (tests update functionality)
test-project-update:
    cd test-generated-api-sqlite && uv run copier update --trust --defaults
