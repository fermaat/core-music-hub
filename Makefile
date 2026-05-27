.PHONY: install install-dev lint format mypy test check clean

install:
	pdm install

install-dev:
	pdm install -d

lint:
	pdm run ruff check src tests

format:
	pdm run black src tests

mypy:
	pdm run mypy src tests

test:
	pdm run pytest -q

check:
	bash run_local_checks.sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml .coverage
