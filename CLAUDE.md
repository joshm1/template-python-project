# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Copier template** for generating modern Python projects. It is NOT a Python project itself - it's a meta-project that generates Python projects using the Copier templating engine.

## Generated Project Capabilities

### Project Types
- **CLI** - Command-line apps with Click + Rich for beautiful terminal output
- **API** - FastAPI REST services with async support, Pydantic v2 validation
- **Library** - Distributable packages with Hatchling build system
- **Monorepo** - UV workspaces with multiple packages

### Database Support
All database options use async drivers for non-blocking I/O:
- **PostgreSQL** - SQLAlchemy 2.0 async + asyncpg driver + Alembic migrations
- **SQLite** - SQLAlchemy 2.0 async + aiosqlite driver + Alembic migrations
- **Supabase** - Official supabase-py client + httpx for async requests
- **None** - No database dependencies

### Type Safety (Pyright Strict)
Generated projects use pyright in strict mode with comprehensive checks:
- All `reportUnknown*Type` checks enabled
- All `reportOptional*` checks enabled
- Unused code detection (`reportUnused*`)
- `reportUnnecessaryTypeIgnoreComment` to catch stale ignores
- Custom stubs directory (`stubs/`) for third-party type overrides

### Testing Infrastructure
- **pytest** with async support via `pytest-asyncio` (mode="auto")
- **pytest-xdist** for parallel test execution (`-n=auto --dist=worksteal`)
- **pytest-timeout** with 20-second default per test
- **pytest-cov** for coverage reporting (API projects)
- **httpx** for testing FastAPI with `AsyncClient`
- Test markers: `unit`, `integration`, `slow`, `e2e`, `supabase`

### CLI Projects (Click)
- Click command groups with `--help` auto-generation
- Rich console output for formatting
- Loguru for structured logging
- Entry point defined in pyproject.toml: `project-slug = "package_name.cli:main"`

### API Projects (FastAPI)
- Async endpoints with `async def`
- Pydantic v2 models for request/response validation
- pydantic-settings for configuration from environment
- Uvicorn ASGI server with hot reload
- Integration tests using `httpx.AsyncClient`

## Common Commands

```bash
# Install template dev dependencies
just install

# Generate a new project (interactive)
just generate /path/to/output

# Generate during development (uses HEAD, allows dirty)
just generate-dev /path/to/output

# Validate template generates successfully
just validate

# Run all template tests
just test-template

# Run fast tests only (no uv sync, no quality checks)
just test-template-fast

# Run generation tests
just test-generation

# Run quality checks (pyright, ruff on generated projects)
just test-quality

# Regenerate the test project (test-generated-api-sqlite)
just test-project-generate

# Run quality checks on the test project
just test-project-quality
```

## Architecture

### Template Files
- `copier.yml` - Template configuration with all variables and choices
- `template/` - Jinja2 template files that get rendered during generation
  - Files ending in `.jinja` are processed by Copier
  - Directory names can contain Jinja2 variables: `{{package_name}}`
  - Conditional files use Jinja2 in filenames: `{% if condition %}file.py{% endif %}.jinja`

### Template Variables (from copier.yml)
Key variables that affect generation:
- `project_type`: cli, api, library, monorepo
- `database_type`: none, postgresql, supabase, sqlite
- `python_version`: "3.12" or "3.13"
- `use_alembic`: Database migrations (auto-derived for postgresql/sqlite)
- `ruff_strictness`: minimal, recommended, strict
- `documentation_tier`: minimal, standard, comprehensive

### Meta-Testing Infrastructure
The template has comprehensive tests that validate generated projects work correctly:

**Test Configurations** (6 total in `tests/fixtures/copier_configs.py`):
- `CLI_SIMPLE` - CLI with no database
- `CLI_WITH_SQLITE` - CLI with SQLite + Alembic
- `API_POSTGRES` - FastAPI + PostgreSQL + Alembic
- `API_SUPABASE` - FastAPI + Supabase
- `API_MINIMAL` - FastAPI with no database
- `LIBRARY_SIMPLE` - Distributable library

**Test Coverage**:
- `test_generation.py` - Template generates without errors, expected files exist, no unrendered Jinja2
- `test_quality_checks.py` - Generated projects pass:
  - `uv sync` - Dependencies install correctly
  - `pyright` - Type checking passes in strict mode
  - `ruff check` - Linting passes
  - `ruff format` - Code is formattable
  - `pytest --collect-only` - Tests can be discovered

### Test Project
- `test-generated-api-sqlite/` - Pre-generated project for quick quality checks
- Uses API + SQLite configuration (exercises most code paths without external services)
- Preserves `.venv` across regenerations for speed

## Test Markers

```bash
# Skip slow tests (uv sync, quality checks)
uv run pytest tests/ -m "not slow"

# Skip Docker tests
uv run pytest tests/ -m "not docker"

# Run specific configuration
uv run pytest tests/ -k "cli_simple"

# Run smoke tests (subset of configs)
uv run pytest tests/ -k "cli_simple or api_postgres or library_simple"
```

## Key Files to Understand

1. **copier.yml** - All template variables, their types, defaults, and conditional visibility
2. **template/pyproject.toml.jinja** - Generated project's dependencies, pyright config, pytest config
3. **template/justfile.jinja** - Generated project's task runner recipes
4. **template/tests/conftest.py.jinja** - Generated project's pytest fixtures and markers
5. **tests/fixtures/copier_configs.py** - All test configurations with expected/excluded files
