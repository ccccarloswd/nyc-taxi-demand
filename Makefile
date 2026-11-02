.PHONY: help install format lint typecheck test check

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Create the virtual env and install git hooks
	uv sync
	uv run pre-commit install

format: ## Auto-format the code
	uv run ruff format .
	uv run ruff check --fix .

lint: ## Check style and common bugs
	uv run ruff format --check .
	uv run ruff check .

typecheck: ## Static type checking
	uv run mypy

test: ## Run the test suite with coverage
	uv run pytest --cov --cov-report=term-missing

check: lint typecheck test ## Everything CI runs
