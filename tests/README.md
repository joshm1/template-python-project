# Template Meta-Testing

This directory contains tests for the Copier template itself (meta-tests). These tests generate projects using different configurations and verify that the generated projects are valid and functional.

## Test Structure

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── fixtures/
│   └── copier_configs.py       # Test configuration matrix
├── test_generation.py          # Basic generation tests
└── test_quality_checks.py      # Code quality tests (uv sync, pyright, ruff)
```

## Running Tests

### Quick Start

```bash
# Run fast tests only (no slow tests)
just test-template-fast

# Run generation tests only
just test-generation

# Run quality checks (pyright, ruff)
just test-quality
```

### All Test Commands

```bash
# Run all tests
just test-template

# Run smoke tests (minimal subset)
just test-template-smoke

# Run tests in parallel
just test-template-parallel

# Run with coverage
just test-template-coverage
```

## Test Configurations

The test suite validates the template against multiple realistic project configurations:

- **CLI_SIMPLE**: Simple CLI tool with no database
- **CLI_WITH_SQLITE**: CLI tool with SQLite database
- **API_POSTGRES**: FastAPI service with PostgreSQL and Alembic
- **API_MINIMAL**: Minimal FastAPI service (no database)
- **LIBRARY_SIMPLE**: Reusable Python library

Each configuration is tested for:
1. Successful template generation
2. Expected files exist / excluded files don't exist
3. Valid pyproject.toml TOML syntax
4. No unrendered Jinja2 templates
5. `uv sync` succeeds
6. Pyright type checking passes
7. Ruff linting passes
8. Ruff formatting is correct

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.slow` - Slow tests (uv sync, quality checks)
- `@pytest.mark.docker` - Requires Docker daemon
- `@pytest.mark.devcontainer` - Requires devcontainer CLI

Skip slow tests:
```bash
pytest tests/ -m "not slow"
```

## Writing New Tests

### Adding a New Configuration

Edit `tests/fixtures/copier_configs.py`:

```python
NEW_CONFIG = TestConfig(
    name="new_config",
    data={
        "project_name": "New Project",
        "project_slug": "new-project",
        "project_type": "cli",
        # ... other template variables
    },
    expected_files=[
        "pyproject.toml",
        "README.md",
        # ... files that must exist
    ],
    excluded_files=[
        "alembic.ini",  # files that must NOT exist
    ],
)

# Add to ALL_CONFIGS
ALL_CONFIGS = [
    CLI_SIMPLE,
    NEW_CONFIG,  # Add here
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

    # Your assertions here
    assert (project_dir / "some_file.py").exists()
```

## CI/CD Integration

These tests should run in CI to ensure template changes don't break project generation.

Recommended CI workflow:
1. Fast tests on every commit
2. Full tests (including slow) on PR
3. Matrix tests across Python versions

## Debugging Failed Tests

### Inspect Generated Projects

Failed tests leave generated projects in `/tmp/copier_test_*` directories.

Generate a project manually for debugging:

```bash
just generate-dev /tmp/debug-project
cd /tmp/debug-project
uv sync
uv run pyright
```

### Common Issues

1. **Jinja2 syntax errors**: Check `test_no_unrendered_jinja_templates`
2. **Missing files**: Check `test_expected_files_exist` output
3. **Type errors**: Run `uv run pyright` in failing project
4. **Import errors**: Check `pyproject.toml` dependencies

## Coverage Goals

- **Generation tests**: 100% of configs
- **Quality checks**: 100% of configs
- **Server tests**: All API configs
- **Docker tests**: All Docker-enabled configs
