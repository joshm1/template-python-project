# Justfile for managing the Python project template
# https://github.com/casey/just

# Default output directory for generated projects
default_output := "../generated"

# Show available recipes
default:
    @just --list

# Generate a new project interactively
generate destination=default_output:
    copier copy . "{{destination}}"

# Generate a new project with dirty changes (useful during template development)
generate-dev destination=default_output:
    copier copy --vcs-ref HEAD . "{{destination}}"

# Generate a project with all defaults (non-interactive, for testing)
generate-defaults destination=default_output name="test-project":
    copier copy --force --defaults -d "project_name={{name}}" . "{{destination}}"

# Generate a project with specific options (non-interactive)
generate-with destination=default_output name="my-project" type="cli" +DATA="":
    copier copy --force -d "project_name={{name}}" -d "project_type={{type}}" {{DATA}} . "{{destination}}"

# Update an existing project generated from this template
update destination:
    copier update "{{destination}}"

# Update with dirty changes (useful during template development)
update-dev destination:
    copier update --vcs-ref HEAD "{{destination}}"

# Validate the template by generating a test project
validate:
    #!/usr/bin/env bash
    set -euo pipefail
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    echo "Generating test project in $TEMP_DIR..."
    copier copy --force --defaults -d "project_name=Template Test" --vcs-ref HEAD . "$TEMP_DIR"
    echo "Template generated successfully!"
    ls -la "$TEMP_DIR"

# Clean generated test projects
clean:
    rm -rf {{default_output}}/*

# Show template questions/configuration
show-config:
    @cat copier.yml
