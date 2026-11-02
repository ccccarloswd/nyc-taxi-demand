# 2. Development environment and tooling

- **Status:** Accepted
- **Date:** 2026-11-02

## Context

The project needs a reproducible environment that runs PySpark reliably and
enforces code quality from the first commit.

## Decision

| Need | Choice | Main alternatives |
|---|---|---|
| OS for development | WSL2 (Ubuntu 24.04) | Native Windows, VM |
| Python & dependencies | uv with a committed `uv.lock` | pip + venv, Poetry, conda |
| Layout | `src/` layout, installable package | flat layout, notebooks only |
| Formatting & linting | ruff | black + flake8 + isort |
| Type checking | mypy (strict) | pyright, none |
| Tests | pytest + coverage | unittest |
| Automation | pre-commit locally, GitHub Actions in CI | CI only |
| Java runtime for Spark | OpenJDK 17 | 21 |

## Rationale

- **WSL2:** Spark on native Windows needs extra binaries (`winutils`) and has path
  and permission issues. WSL2 gives near-native Linux performance, matching the
  environment the code would run on in production.
- **uv:** one fast tool for Python versions, virtual envs and locked dependencies,
  so local runs and CI install exactly the same versions.
- **`src/` layout:** tests run against the installed package, not against whatever
  happens to be in the working directory, which catches packaging mistakes early.
- **ruff:** replaces several tools with one, and is fast enough to run on every commit.
- **Strict mypy:** data pipelines pass many DataFrames and configs between functions;
  types catch wrong arguments before a long Spark job fails at runtime.
- **Local pre-commit hooks** call `uv run`, so the tool versions come from `uv.lock`
  and never drift from CI.

## Consequences

- Contributors need Linux, macOS or WSL2 plus uv and Java 17.
- Code must pass formatting, linting, type checks and tests before it is merged.
