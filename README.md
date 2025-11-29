# Modern Python Project Template

An opinionated Copier template for Python projects. This is my personal setup for new projects - maybe you'll find it useful too.

## Features

- **Project Types**: CLI (Click + Rich), API (FastAPI), Library, Monorepo (UV workspaces)
- **Database Support**: PostgreSQL, SQLite, Supabase - all with async drivers
- **Strict Typing**: Pyright in strict mode with comprehensive checks
- **Async Testing**: pytest-asyncio, pytest-xdist (parallel), httpx for API tests
- **Modern Tooling**: UV package manager, Ruff linter/formatter, pre-commit hooks
- **Docker**: Multi-stage builds, docker-compose, VS Code devcontainer
- **Claude Code**: Custom agents, slash commands, skills, MCP servers

## Quick Start

```bash
# Install Copier
uv tool install copier

# Generate a new project
copier copy gh:joshm1/template-python-project /path/to/new/project

# Or use locally during development
copier copy /path/to/template-python-project /path/to/new/project
```

## Project Types

| Type | Stack |
|------|-------|
| **CLI** | Click + Rich + Loguru |
| **API** | FastAPI + Pydantic v2 + Uvicorn |
| **Library** | Hatchling build system |
| **Monorepo** | UV workspaces |

## Database Options

| Database | Driver | Migrations |
|----------|--------|------------|
| PostgreSQL | SQLAlchemy 2.0 + asyncpg | Alembic |
| SQLite | SQLAlchemy 2.0 + aiosqlite | Alembic |
| Supabase | supabase-py + httpx | Supabase migrations |

## Always Included

- **Pyright** strict mode with all `reportUnknown*` and `reportOptional*` checks
- **pytest** with async support, parallel execution, timeout protection
- **Ruff** for linting and formatting
- **pre-commit** hooks
- **justfile** task runner
- **Docker** and VS Code devcontainer
- **Claude Code** integration

## Configuration Options

| Option | Choices |
|--------|---------|
| Python version | 3.12, 3.13 |
| Database | None, PostgreSQL, SQLite, Supabase |
| Ruff strictness | minimal, recommended, strict |
| Documentation | minimal, standard, comprehensive |

## Development

```bash
# Install dependencies
just install

# Generate test project
just generate-dev /tmp/test-project

# Run template tests
just test-template

# Run fast tests only
just test-template-fast
```

## Template Testing

The template includes meta-tests that validate generated projects:

- Template generates without errors
- All expected files exist
- `uv sync` installs dependencies
- `pyright` passes in strict mode
- `ruff check` and `ruff format` pass
- `pytest` can collect tests

## License

Proprietary - All rights reserved.
