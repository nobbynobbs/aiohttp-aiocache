.PHONY: tests

install:
	poetry install

tests:
	poetry run pytest tests -v

tests-cov:
	poetry run pytest -v --cov=aiohttp_aiocache tests

tests-cov-report:
	poetry run pytest -v --cov=aiohttp_aiocache --cov-report=html tests

lint:
	poetry run flake8 --exclude .venv

mypy:
	poetry run mypy -p aiohttp_aiocache
	poetry run mypy tests
