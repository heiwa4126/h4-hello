# AI Coding Agent Instructions for h4-hello

## Project Overview
This is a practice project for publishing Python packages to PyPI with PEP740 digital signatures using **uv** as the build backend and package manager. The project contains only a simple `hello()` function but demonstrates modern Python packaging workflows with Trusted Publishing and Sigstore attestations.

## Architecture & Key Components

### Package Structure
- `src/h4_hello/` - Source package using src-layout pattern
- `hello.py` - Core function implementation
- `main.py` - CLI entry point (exposed as `h4-hello` command)
- `hello_test.py` - Co-located test files (excluded from builds via `tool.uv.build-backend`)

### Build System
- **uv** as build backend (`uv_build`) - NOT setuptools/hatchling
- Uses modern `pyproject.toml` configuration exclusively
- Test files auto-excluded via `source-exclude` and `wheel-exclude` patterns

## Development Workflows

### Task Management with poethepoet
Use `poe <task>` commands defined in `poe_tasks.toml`:
```bash
poe test          # Run pytest tests
poe check         # Ruff linting
poe mypy          # Type checking
poe format        # Auto-format code
poe before        # Full pre-commit checks
poe testpypi      # Deploy to TestPyPI (requires .env)
```

### Build & Test Workflow
```bash
# Pre-build validation
poe before        # Runs check, format, mypy, tests, pyproject validation

# Build packages
uv build          # Creates both .tar.gz and .whl in dist/

# Smoke test built packages
uv run --isolated --no-project --with "dist/*.whl" src/h4_hello/main.py
uv run --isolated --no-project --with "dist/*.tar.gz" src/h4_hello/main.py
```

### Publishing Strategy
- **TestPyPI**: Tag with `test-*` (e.g., `test-0.1.11`) triggers TestPyPI deployment
- **PyPI**: Tag with `v*` semver (e.g., `v0.1.11`) triggers PyPI deployment
- Both use GitHub Actions with Trusted Publishing (no manual tokens)

## Project-Specific Patterns

### Version Management
- Manual version bumps in `pyproject.toml` (no automated versioning)
- Beta versions supported: `0.1.12-beta1`
- Git tags should match pyproject.toml version

### Testing & Quality
- Tests use simple assert statements (no complex frameworks)
- Co-located test files (`*_test.py`) automatically excluded from builds
- Strict tooling: ruff, mypy, actionlint for workflows

### Security & Publishing
- **Trusted Publishing only** - no API tokens in workflows
- Owner-only publishing: `if: github.repository_owner == github.actor`
- PEP740 Sigstore attestations enabled by default
- Environment-based deployment gates (`environment: testpypi/pypi`)

## Key Configuration Files

### `pyproject.toml`
- Uses `uv_build` backend (not setuptools)
- CLI entry point: `h4-hello = "h4_hello:main"`
- Build exclusions handle test files

### `poe_tasks.toml`
- Executor set to `uv` (not default Python)
- Environment variables for commands
- Grouped tasks for complex workflows

### GitHub Actions
- Reusable workflow pattern: `build-package.yml` called by publish workflows
- Pinned action versions with commit SHAs (security best practice)
- Artifact-based build/publish separation

## Integration Points
- **uv** for all Python operations (no pip/poetry mixing)
- **poethepoet** for task running (not make/npm scripts)
- **GitHub Actions** with OIDC for publishing (no manual secrets)
- **TestPyPI** for validation before PyPI release

## Common Pitfalls
- Don't use `pip install -e .` - use `uv sync` for development
- Build backend is `uv_build`, not `setuptools.build_meta`
- Test files are excluded via pyproject.toml, not .gitignore
- Publishing requires repository owner permissions (security feature)
