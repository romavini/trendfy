setup:
	python -m venv venv
	venv/bin/pip install -e .
	venv/bin/pip install -r requirements-dev.txt

run:
	docker-compose up -d

check:
	venv/bin/python -m isort trendfy/ tests/
	venv/bin/python -m black trendfy/ tests/
	venv/bin/python -m pylint --rcfile=pyproject.toml trendfy/ tests/
	venv/bin/python -m mypy --config-file pyproject.toml trendfy/ tests/
	venv/bin/python -m flake8 trendfy/ tests/
	venv/bin/python -m flake8 *.md Makefile --select=W291
	venv/bin/python -m xenon trendfy/ --max-absolute A --max-modules A --max-average A
	venv/bin/python -m xenon tests/ --no-assert --max-absolute A --max-modules A --max-average A
	venv/bin/python -m bandit -q -r trendfy/
	venv/bin/python -m bandit -s=B101 -q -r tests/

check2build:
	venv/bin/python -m isort --check-only trendfy/ tests/
	venv/bin/python -m black --check trendfy/ tests/
	venv/bin/python -m pylint --rcfile=pyproject.toml trendfy/ tests/
	venv/bin/python -m mypy --config-file pyproject.toml trendfy/ tests/
	venv/bin/python -m xenon trendfy/ --max-absolute A --max-modules A --max-average A
	venv/bin/python -m xenon tests/ --no-assert --max-absolute A --max-modules A --max-average A
	venv/bin/python -m bandit -q -r trendfy/
	venv/bin/python -m bandit -s=B101 -q -r tests/

test:
	venv/bin/python -m pytest -l -s -vvv tests/ --cov trendfy/ --cov-fail-under=90 --cov-report xml --cov-report term:skip-covered

all: check test
