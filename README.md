# Modern Python Project Template

A production-ready Copier template for Python projects, based on analysis of 40+ real-world Python projects.

## Features

- **Multiple Project Types**: CLI tools, API services, libraries, and monorepos
- **Modern Tooling**: UV package manager, Ruff linter, Pyright type checker
- **Testing Infrastructure**: pytest with comprehensive fixtures and markers
- **Docker Support**: Multi-stage builds with docker-compose
- **Database Options**: PostgreSQL, Supabase, SQLite
- **Claude Code Integration**: Custom agents, slash commands, skills, and MCP servers
- **Tiered Documentation**: Minimal, standard, or comprehensive documentation levels

## Quick Start

```bash
# Install Copier and required extensions
uv tool install copier
pip install copier-templates-extensions  # Required for git config defaults

# Generate a new project
copier copy gh:joshm1/template-python-project /path/to/new/project

# Or use the local template during development
copier copy /path/to/template-python-project /path/to/new/project
```

> **Note:** The `copier-templates-extensions` package is required for author name/email to default to your `git config user.name` and `git config user.email` values.

## Template Structure

```
template-python-project/
├── copier.yml              # Template configuration (186 lines)
├── template/               # Template files
│   └── {{project_slug}}/   # Generated project root
│       ├── .devcontainer/  # VS Code devcontainer
│       ├── .github/        # GitHub Actions workflows
│       ├── .claude/        # Claude Code configuration
│       │   ├── agents/     # Custom agents
│       │   ├── commands/   # Slash commands
│       │   └── skills/     # Skills
│       ├── src/            # Source code
│       │   └── {{package_name}}/
│       │       ├── api/    # API routes (for API projects)
│       │       ├── core/   # Core configuration
│       │       ├── models/ # Database models
│       │       ├── repositories/ # Repository pattern
│       │       └── schemas/ # Pydantic schemas
│       ├── tests/          # Test files
│       │   ├── unit/
│       │   ├── integration/
│       │   ├── fixtures/
│       │   └── data/
│       ├── docs/           # Documentation
│       │   ├── agent/      # AI agent docs
│       │   └── code-style/ # Code style guides
│       ├── alembic/        # Database migrations
│       ├── supabase/       # Supabase configuration
│       ├── packages/       # Monorepo packages
│       ├── scripts/        # Utility scripts
│       └── stubs/          # Type stubs
└── README.md               # This file
```

## Supported Project Types

### CLI Tool
Command-line applications using Click, with rich terminal output.

### API Service
FastAPI-based REST APIs with optional database integration.

### Library
Distributable Python packages with proper packaging metadata.

### Monorepo
Multi-package workspaces with shared dependencies.

## Configuration Options

### Always Included (Not Configurable)
- Pyright strict type checking
- pytest testing infrastructure
- pre-commit hooks
- justfile task runner
- Claude Code integration (commands, agents, skills, MCP servers)
- rich terminal output
- Click for CLI projects
- Hatchling build system
- VS Code devcontainer

### Configurable Options

**Basic Information:**
- Project name, slug, and package name
- Author name and email (defaults to git config)
- Project description

**Project Type:**
- CLI Tool, API Service, Library, or Monorepo (UV workspaces)

**Python Configuration:**
- Python version (3.12 or 3.13)

**Infrastructure:**
- Docker and docker-compose (default: enabled)
- Database type (None, PostgreSQL, Supabase, SQLite)
- Alembic migrations (for PostgreSQL)
- Local Supabase stack

**Development Tools:**
- Ruff strictness (minimal/recommended/strict)
- Dependency pinning strategy (flexible/conservative/strict)

**Documentation:**
- Documentation tier (minimal/standard/comprehensive)

## Development Tools

All generated projects include:

- **UV**: Fast Python package manager
- **Ruff**: Lightning-fast linter and formatter
- **Pyright**: Static type checker (strict mode)
- **pytest**: Testing framework with parallel execution
- **pre-commit**: Git hooks for code quality
- **just**: Command runner (replaces Make)

## Planning Documentation

See the planning documents in the parent directory for detailed information:

- `COPIER-TEMPLATE-PLAN-v2.md`: Overview and navigation
- `plan/02-variables.md`: Template variable definitions
- `plan/03-directory-structure.md`: Directory layouts by project type
- `plan/04-*.md`: Individual file templates and configurations

## Next Steps

After creating the base structure, the following template files need to be implemented:

1. Core configuration files (pyproject.toml, pyrightconfig.json, .gitignore)
2. Documentation templates (CLAUDE.md, README.md, docs/)
3. Claude Code integration (.claude/*)
4. Build and task files (justfile, Dockerfile, docker-compose.yml)
5. Testing infrastructure (conftest.py, pytest configuration)
6. CI/CD workflows (.github/workflows/)
7. Development environment (devcontainer)

## License

MIT
