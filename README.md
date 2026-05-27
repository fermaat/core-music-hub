# Python Package Template

A lightweight, opinionated template for new Python projects.

It ships with:
- `pyproject.toml` (PDM, `src/` layout, `pdm-backend`)
- `core-utils` wired in as a base dependency (shared `CoreSettings`, logger,
  profiler)
- `settings.py` subclassing `CoreSettings`
- Tooling: `ruff`, `black`, `mypy`, `pytest` + coverage
- Local validation (`run_local_checks.sh`) and GitHub Actions CI

## Quick start

1. Create your new repo from this template (or copy its contents into it).
2. Rename the package `src/package_name/` → `src/<your_package>/` and update
   every `package_name` / `package-name` reference:
   - `[project].name` in `pyproject.toml`
   - `[tool.ruff.lint.isort].known-first-party`
   - imports in `tests/`
3. Fill in `[project]` metadata in `pyproject.toml`: `description`, `version`,
   `authors`; add runtime dependencies to `[project].dependencies`.
4. Add project-specific fields in `src/<your_package>/settings.py`.
5. Install and validate:

   ```bash
   make install-dev
   make check
   ```

## Layout

```
src/<package>/      package code
  settings.py       Settings(CoreSettings) — env + .env loading
  py.typed          PEP 561 marker (ships type hints)
tests/
  unit/             unit tests
  integration/      integration tests
  conftest.py       shared fixtures
.github/workflows/  CI: ruff + black + mypy + pytest
```

## Dependencies

Runtime deps are intentionally minimal: `core-utils`, `pydantic`,
`pydantic-settings`. Add what each project needs — note `loguru` and `pyyaml`
are already available transitively through `core-utils`.
