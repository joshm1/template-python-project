#!/usr/bin/env python3
"""Automate copier update workflow: stash, update, verify."""

import subprocess
import sys
from pathlib import Path

import click


def run(
    cmd: str, cwd: Path | None = None, check: bool = True, capture: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a shell command."""
    click.echo(click.style(f"$ {cmd}", fg="cyan"))
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    if capture:
        if result.stdout:
            click.echo(result.stdout.rstrip())
        if result.stderr:
            click.echo(result.stderr.rstrip(), err=True)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def get_template_dir() -> Path:
    """Get the template directory (parent of scripts/)."""
    return Path(__file__).parent.parent.resolve()


def check_template_clean(template_dir: Path) -> None:
    """Abort if template has uncommitted changes."""
    result = run("git status --porcelain", cwd=template_dir, check=False)
    if result.stdout.strip():
        click.echo(click.style("\n❌ Template has uncommitted changes:", fg="red"))
        click.echo(result.stdout)
        click.echo(click.style("\nPlease commit your template changes first:", fg="yellow"))
        click.echo("  git add <files>")
        click.echo('  git commit -m "feat: <description>"')
        click.echo("\nSemantic commit prefixes: feat, fix, refactor, docs, chore, test")
        sys.exit(1)


@click.command()
@click.option(
    "-p",
    "--project",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to the project to update",
)
def main(project: Path) -> None:
    """Stash changes, run copier update, and verify with pyright + tests."""
    template_dir = get_template_dir()
    project = project.resolve()

    click.echo(f"Template: {template_dir}")
    click.echo(f"Project:  {project}")

    # Check template is clean first
    click.echo(click.style("\n=== Checking template status ===", bold=True))
    check_template_clean(template_dir)
    click.echo(click.style("✓ Template is clean", fg="green"))

    # Check if project has changes to stash
    status = run("git status --porcelain", cwd=project, check=False)
    needs_stash = bool(status.stdout.strip())

    if needs_stash:
        click.echo(click.style("\n=== Stashing project changes ===", bold=True))
        run("git stash -u", cwd=project)

    click.echo(click.style("\n=== Running copier update ===", bold=True))
    result = run("copier update --defaults --trust", cwd=project, check=False)

    if result.returncode != 0:
        click.echo(click.style("\n❌ Copier update failed", fg="red"))
        if needs_stash:
            click.echo("Restoring stash...")
            run("git stash pop", cwd=project, check=False)
        sys.exit(1)

    click.echo(click.style("\n=== Running pyright ===", bold=True))
    pyright_result = run("uv run pyright", cwd=project, check=False)

    click.echo(click.style("\n=== Running tests ===", bold=True))
    test_result = run("uv run pytest -v", cwd=project, check=False)

    # Summary
    click.echo("\n" + "=" * 50)
    if pyright_result.returncode == 0 and test_result.returncode == 0:
        click.echo(click.style("✓ Copier update successful - all checks pass", fg="green"))
    else:
        click.echo(click.style("❌ Issues found:", fg="red"))
        if pyright_result.returncode != 0:
            click.echo("  - pyright failed")
        if test_result.returncode != 0:
            click.echo("  - tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
