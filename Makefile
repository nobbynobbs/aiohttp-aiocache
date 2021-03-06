.PHONY: tests build

install:
	poetry install

tests:
	poetry run pytest tests -v

tests-cov:
	poetry run pytest -v --cov=aiohttp_aiocache tests

tests-cov-report:
	poetry run pytest -v --cov=aiohttp_aiocache --cov-report=xml tests

lint:
	poetry run flake8 --exclude .venv

mypy:
	poetry run mypy -p aiohttp_aiocache
	poetry run mypy tests

build:
	poetry build

publish:
	poetry publish -u $(PYPI_LOGIN) -p $(PYPI_PASSWORD)
