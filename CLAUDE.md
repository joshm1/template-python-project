# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Copier template** for generating modern Python projects. It is NOT a Python project itself - it's a meta-project that generates Python projects using the Copier templating engine.

The template generates projects with:
- UV package manager
- Pyright strict type checking
- pytest with comprehensive fixtures
- Docker and devcontainer support
- FastAPI (for API projects)
- Claude Code integration (.claude/ with commands, agents, skills)

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
Tests validate the template generates working projects:
- `tests/fixtures/copier_configs.py` - Test configuration matrix (6 configs)
- `tests/test_generation.py` - Basic generation tests (fast)
- `tests/test_quality_checks.py` - Quality checks: pyright, ruff (slow)
- `tests/conftest.py` - Shared fixtures including pre-generated test project

### Test Project
- `test-generated-api-sqlite/` - Pre-generated project for quick quality checks
- Uses API + SQLite configuration (exercises most code paths)
- Preserves `.venv` across regenerations for speed

## Test Markers

```bash
# Skip slow tests (uv sync, quality checks)
uv run pytest tests/ -m "not slow"

# Skip Docker tests
uv run pytest tests/ -m "not docker"

# Run specific configuration
uv run pytest tests/ -k "cli_simple"
```

## Key Files to Understand

1. **copier.yml** - All template variables, their types, defaults, and when they appear
2. **template/pyproject.toml.jinja** - Generated project's dependencies and configuration
3. **template/justfile.jinja** - Generated project's task runner recipes
4. **tests/fixtures/copier_configs.py** - All test configurations with expected/excluded files
