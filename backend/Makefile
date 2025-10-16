.PHONY: help install dev-install format lint type-check test test-cov clean run-dev run-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	uv pip install --system -r requirements.txt

dev-install: ## Install development dependencies
	uv pip install --system -r requirements.txt
	uv pip install --system -e ".[dev]"

format: ## Format code with ruff
	ruff format .
	ruff check . --fix

lint: ## Lint code with ruff
	ruff check .

type-check: ## Type check with mypy
	mypy .

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=term-missing --cov-report=html

clean: ## Clean cache and temp files
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run-dev: ## Run development server
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run production server
	uvicorn main:app --host 0.0.0.0 --port 8000

check-all: format lint type-check test ## Run all checks (format, lint, type-check, test)

ci: lint type-check test ## Run CI checks (no formatting)
