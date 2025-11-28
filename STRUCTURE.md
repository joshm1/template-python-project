# Template Structure Summary

This document describes the base Copier template structure that has been created.

## Created Files

### Root Level

```
/path/to/template-python-project/
├── copier.yml          # Copier configuration
├── README.md           # Template documentation
├── STRUCTURE.md        # This file
└── template/           # Template files (rendered to project root)
```

## copier.yml Configuration

The main template configuration file includes:

### Template Variables (20 total)

#### Basic Project Info (4)
- `project_name`: Human-readable project name
- `project_slug`: URL-friendly project identifier (auto-generated)
- `package_name`: Python package name (auto-generated)
- `description`: Project description

#### Project Type (1)
- `project_type`: cli/api/library/monorepo

#### Python Configuration (2)
- `python_version`: 3.12 or 3.13
- `use_hatchling`: Build system choice

#### Infrastructure (3)
- `database_type`: none/postgresql/supabase/sqlite
- `use_alembic`: Database migrations
- `use_supabase_local`: Local Supabase stack

Note: Docker and DevContainers are ALWAYS included (not configurable).

#### Development Tools (5)
- `ruff_strictness`: minimal/recommended/strict
- `dependency_pinning`: flexible/conservative/strict
- `enable_type_checking`: Pyright configuration
- `enable_testing`: pytest infrastructure
- `documentation_tier`: minimal/standard/comprehensive

#### Claude Code Integration (5)
- `setup_claude_code`: Enable Claude Code support
- `include_slash_commands`: Slash commands
- `include_custom_agents`: Custom agents
- `include_skills`: Skills
- `include_mcp_servers`: MCP server configurations

#### Git Configuration (1)
- `git_init`: Initialize git repository

### Template Configuration

- `_min_copier_version`: "9.0.0"
- `_templates_suffix`: ".jinja"
- `_exclude`: Files to exclude from template
- `_tasks`: Post-generation hooks (git init, add, commit)

## Template Directory Structure

The `template/` directory contains the complete skeleton for all project types:

### Directory Count: 43 directories

#### Claude Code Integration (3 + root)
```
.claude/
├── agents/       # Custom agents (.gitkeep)
├── commands/     # Slash commands (.gitkeep)
└── skills/       # Skills (.gitkeep)
```

#### Development Environment (1 + root)
```
.devcontainer/    # VS Code devcontainer (.gitkeep)
```

#### CI/CD (1 + subdirs)
```
.github/
└── workflows/    # GitHub Actions (.gitkeep)
```

#### Source Code (5 + subdirs)
```
src/
└── {{package_name}}/
    ├── api/
    │   └── routes/       # API endpoints (.gitkeep)
    ├── core/             # Core configuration (.gitkeep)
    ├── models/           # Database models (.gitkeep)
    ├── repositories/     # Repository pattern (.gitkeep)
    └── schemas/          # Pydantic schemas (.gitkeep)
```

#### Testing (4 + root)
```
tests/
├── unit/          # Unit tests (.gitkeep)
├── integration/   # Integration tests (.gitkeep)
├── fixtures/      # Test fixtures (.gitkeep)
└── data/          # Test data (.gitkeep)
```

#### Documentation (2 + root)
```
docs/
├── agent/         # AI agent documentation (.gitkeep)
└── code-style/    # Code style guides (.gitkeep)
```

#### Database Migrations (1 + subdirs)
```
alembic/
└── versions/      # Migration files (.gitkeep)
```

#### Supabase (3 + subdirs)
```
supabase/
├── migrations/    # SQL migrations (.gitkeep)
└── volumes/
    ├── db/        # Database data (.gitkeep)
    ├── storage/   # File storage (.gitkeep)
    └── api/       # API data (.gitkeep)
```

#### Monorepo Packages (6 + subdirs)
```
packages/
├── {{package_name}}_common/
│   ├── src/
│   │   └── {{package_name}}_common/  # Common code (.gitkeep)
│   └── tests/                         # Common tests (.gitkeep)
└── {{package_name}}_api/
    ├── src/
    │   └── {{package_name}}_api/      # API code (.gitkeep)
    └── tests/                          # API tests (.gitkeep)
```

#### Scripts (1 + subdirs)
```
scripts/
└── tasks/         # Task scripts (.gitkeep)
```

#### Type Stubs (1)
```
stubs/             # Custom type stubs (.gitkeep)
```

## Placeholder Files

- **Total .gitkeep files**: 27
- **Purpose**: Ensure empty directories are tracked in git

## Jinja2 Variables in Directory Names

The template uses Jinja2 variables for dynamic directory naming:

- `{{package_name}}`: Python package name (e.g., "my_project")

These will be replaced with actual values during template generation. The `project_slug` is used for the output directory name when running `copier copy`.

## Next Steps

The following template files need to be created in the `template/` directory:

### Core Configuration Files
- [ ] `pyproject.toml.jinja` - Python project configuration
- [ ] `pyrightconfig.json.jinja` - Type checking configuration
- [ ] `.gitignore.jinja` - Git ignore patterns
- [ ] `.pre-commit-config.yaml.jinja` - Pre-commit hooks
- [ ] `uv.lock` (conditionally generated)

### Documentation
- [ ] `README.md.jinja` - Project README
- [ ] `CLAUDE.md.jinja` - Claude AI agent documentation
- [ ] `docs/README.md.jinja` - Documentation hub
- [ ] `docs/agent/quick_reference.md.jinja` - Quick reference
- [ ] `docs/agent/documentation_mapping.md.jinja` - Documentation map
- [ ] `docs/code-style/*.md.jinja` - Code style guides

### Build and Task Files
- [ ] `justfile.jinja` - Task runner recipes
- [ ] `Dockerfile.jinja` - Multi-stage Docker build
- [ ] `docker-compose.yml.jinja` - Docker compose configuration
- [ ] `.dockerignore.jinja` - Docker ignore patterns

### Claude Code Configuration
- [ ] `.claude/settings.json.jinja` - Claude settings
- [ ] `.claude/commands/*.md.jinja` - Slash commands
- [ ] `.claude/agents/*.md.jinja` - Custom agents
- [ ] `.claude/skills/*.md.jinja` - Skills
- [ ] `.mcp.json.jinja` - MCP server configuration

### Testing
- [ ] `tests/conftest.py.jinja` - pytest configuration
- [ ] `tests/unit/test_example.py.jinja` - Example unit test
- [ ] `tests/integration/test_example.py.jinja` - Example integration test

### CI/CD
- [ ] `.github/workflows/ci.yml.jinja` - CI workflow
- [ ] `.github/workflows/deploy.yml.jinja` - Deploy workflow (conditional)

### Database
- [ ] `alembic.ini.jinja` - Alembic configuration
- [ ] `alembic/env.py.jinja` - Alembic environment
- [ ] `alembic/script.py.mako.jinja` - Alembic script template
- [ ] `supabase/config.toml.jinja` - Supabase configuration

### Development Environment
- [ ] `.devcontainer/devcontainer.json.jinja` - Devcontainer config
- [ ] `.devcontainer/Dockerfile.jinja` - Devcontainer Dockerfile
- [ ] `.devcontainer/docker-compose.yml.jinja` - Devcontainer compose
- [ ] `.devcontainer/post-create.sh.jinja` - Post-create script

### Environment Files
- [ ] `.env.example.jinja` - Environment variables template
- [ ] `.env.dev.jinja` - Development environment (conditional)
- [ ] `.env.test.jinja` - Test environment (conditional)

### Source Code Templates
- [ ] `src/{{package_name}}/__init__.py.jinja` - Package init
- [ ] `src/{{package_name}}/py.typed` - PEP 561 marker
- [ ] `src/{{package_name}}/cli.py.jinja` - CLI entry point (conditional)
- [ ] `src/{{package_name}}/main.py.jinja` - FastAPI app (conditional)
- [ ] `src/{{package_name}}/core/config.py.jinja` - Configuration
- [ ] `src/{{package_name}}/core/database.py.jinja` - Database setup (conditional)

## Template Generation Test

To test the template:

```bash
# Generate a test project
copier copy /path/to/template-python-project /tmp/test-project

# Check generated structure
cd /tmp/test-project
ls -la
```

## Conditional Directory Inclusion

Some directories should only appear in certain project types:

- `.devcontainer/` - ALWAYS included (Docker and DevContainers are not configurable)
- `alembic/` - if `use_alembic`
- `supabase/` - if `database_type == 'supabase'`
- `packages/` - if `project_type == 'monorepo'`
- `.claude/` - if `setup_claude_code`
- `docs/code-style/` - if `documentation_tier in ['standard', 'comprehensive']`

These will be handled through Jinja2 conditionals in the file templates.
