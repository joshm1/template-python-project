# Meta-Testing Infrastructure

This document describes the meta-testing infrastructure for the Copier template. These tests validate that the template generates working projects across all configuration combinations.

## Overview

The meta-testing infrastructure tests the **template itself** (not the generated projects). It:

1. Generates projects using different configurations
2. Validates the generated project structure
3. Runs quality checks (pyright, ruff, pytest) on generated projects
4. Ensures all generated projects are production-ready

## File Structure

```
template-python-project/
├── pyproject.toml                    # Template project dependencies
├── justfile                          # Test runner recipes
└── tests/                            # Meta-tests
    ├── __init__.py
    ├── conftest.py                   # Shared fixtures
    ├── fixtures/
    │   ├── __init__.py
    │   └── copier_configs.py         # Test configuration matrix
    ├── test_generation.py            # Basic generation tests
    └── test_quality_checks.py        # Quality checks (slow)
```

## Test Configurations

The test suite validates 5 configurations (from `tests/fixtures/copier_configs.py`):

### CLI Configurations
- **CLI_SIMPLE**: Simple CLI tool with no database
- **CLI_WITH_SQLITE**: CLI tool with SQLite database

### API Configurations
- **API_POSTGRES**: FastAPI service with PostgreSQL and Alembic
- **API_MINIMAL**: Minimal FastAPI service (no database)

### Library Configurations
- **LIBRARY_SIMPLE**: Reusable Python library

Each configuration specifies:
- Template variables (project_type, database_type, etc.)
- Expected files that must exist
- Excluded files that must NOT exist
- Test flags (skip_docker, skip_server)

## Running Tests

### Quick Commands

```bash
# Run fast tests only (no uv sync, no quality checks)
just test-template-fast

# Run all generation tests
just test-generation

# Run quality checks (slow: uv sync, pyright, ruff)
just test-quality
```

### All Available Commands

```bash
just test-template              # Run all tests
just test-template-fast         # Fast tests only
just test-template-smoke        # Minimal subset
just test-generation            # Generation tests
just test-quality               # Quality checks
just test-template-parallel     # Parallel execution
just test-template-coverage     # With coverage report
```

### Direct pytest Usage

```bash
# Run specific test
uv run pytest tests/test_generation.py::test_template_generates_successfully -v

# Run for specific config
uv run pytest tests/ -k "cli_simple" -v

# Skip slow tests
uv run pytest tests/ -m "not slow" -v

# Run with verbose output
uv run pytest tests/ -vv --tb=short
```

## Test Categories

### 1. Generation Tests (`test_generation.py`)

Fast tests that verify basic template generation:

- `test_template_generates_successfully` - Template generates without errors
- `test_expected_files_exist` - Required files are created
- `test_excluded_files_not_present` - Unwanted files are not created
- `test_pyproject_is_valid_toml` - pyproject.toml is valid TOML
- `test_no_unrendered_jinja_templates` - No leftover Jinja2 syntax

### 2. Quality Checks (`test_quality_checks.py`)

Slow tests that validate generated project quality:

- **TestUVSync**
  - `test_uv_sync_succeeds` - Dependencies install successfully

- **TestPyright**
  - `test_pyright_passes` - Type checking passes

- **TestRuff**
  - `test_ruff_check_passes` - Linting passes
  - `test_ruff_format_check` - Code is properly formatted

All quality check tests are marked with `@pytest.mark.slow`.

## Test Markers

Tests use pytest markers for selective execution:

```python
@pytest.mark.slow          # Slow tests (uv sync, quality checks)
@pytest.mark.docker        # Requires Docker daemon
@pytest.mark.devcontainer  # Requires devcontainer CLI
```

Usage:
```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Only run slow tests
pytest tests/ -m "slow"

# Skip Docker tests
pytest tests/ -m "not docker"
```

## Writing Tests

### Adding a New Configuration

Edit `tests/fixtures/copier_configs.py`:

```python
NEW_CONFIG = TestConfig(
    name="new_config",
    data={
        "project_name": "New Project",
        "project_slug": "new-project",
        "package_name": "new_project",
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
        "README.md",
    ],
    excluded_files=[
        "alembic.ini",
    ],
)

# Add to ALL_CONFIGS
ALL_CONFIGS = [
    # ... existing configs
    NEW_CONFIG,
]
```

### Adding a New Test

Tests use `@pytest.mark.parametrize` to run against all configurations:

```python
@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c.name)
def test_new_feature(template_path, temp_dir, config):
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

    # Your assertions
    assert (project_dir / "some_file.py").exists()
```

## Fixtures

### Core Fixtures (from `conftest.py`)

- **template_path** - Path to the template directory
- **temp_dir** - Temporary directory for test output
- **generated_project** - Auto-generated project (parametrized)
- **run_in_project** - Helper to run commands in generated project
- **docker_available** - Whether Docker is available
- **devcontainer_cli_available** - Whether devcontainer CLI is available

### Example Usage

```python
def test_example(template_path, temp_dir, config):
    # Generate project
    project_dir = temp_dir / str(config.data["project_slug"])
    copier.run_copy(str(template_path), str(project_dir), data=config.data)

    # Assertions
    assert (project_dir / "pyproject.toml").exists()
```

## Debugging

### Inspect Generated Projects

Failed tests generate projects in `/tmp/copier_test_*`:

```bash
# Find recent test projects
ls -lt /tmp/copier_test_* | head -5

# Inspect a test project
cd /tmp/copier_test_xyz123/test-cli-tool
cat pyproject.toml
uv sync
uv run pyright
```

### Generate Project Manually

```bash
# Generate for debugging
just generate-dev /tmp/debug-project

cd /tmp/debug-project
uv sync
uv run pyright
```

### Common Failures

1. **Expected file missing**
   - Check template has the file
   - Verify Jinja2 conditionals are correct
   - Update `expected_files` list if intentional

2. **Unrendered Jinja2 templates**
   - Check for typos in variable names
   - Verify all variables are defined in copier.yml
   - Look for missing `{% endif %}` or `{% endfor %}`

3. **Pyright failures**
   - Run pyright in generated project
   - Check for missing type stubs
   - Verify imports are correct

4. **Ruff failures**
   - Run ruff in generated project
   - Check template files are formatted
   - Verify generated code follows style guide

## CI/CD Integration

Recommended workflow:

```yaml
# .github/workflows/test-template.yml
name: Test Template

on: [push, pull_request]

jobs:
  test-fast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest tests/ -m "not slow"

  test-full:
    needs: test-fast
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest tests/ -v
```

## Dependencies

Test dependencies (in `pyproject.toml`):

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",           # Test framework
    "pytest-asyncio>=0.24",  # Async test support
    "pytest-timeout>=2.3",   # Test timeouts
    "pytest-xdist>=3.5",     # Parallel execution
    "httpx>=0.28",           # HTTP client for server tests
    "pyyaml>=6.0",           # YAML parsing
    "copier>=9.4",           # Template engine
    "docker>=7.0",           # Docker SDK
]
```

## Coverage Goals

Before releasing a template version, ensure:

- [ ] All generation tests pass (100% of configs)
- [ ] All quality checks pass (100% of configs)
- [ ] `uv sync` succeeds for all configs
- [ ] Pyright passes for all configs
- [ ] Ruff passes for all configs
- [ ] No unrendered Jinja2 templates

## Next Steps

To complete the meta-testing infrastructure, add:

1. **Server tests** (`test_fastapi.py`) - Test FastAPI servers start and respond
2. **Docker tests** (`test_docker.py`) - Test docker-compose up/down
3. **Devcontainer tests** (`test_devcontainer.py`) - Test devcontainer build/exec

See `/path/to/plan/08-testing-strategy.md` for full implementation details.
