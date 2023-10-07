SHELL := /bin/bash
setup:
	python -m venv venv
	venv/bin/pip install -e .
	venv/bin/pip install -r requirements-dev.txt

run:
	docker-compose up -d

lint:
	venv/bin/python -m isort trendfy/
	venv/bin/python -m black trendfy/

check:
	venv/bin/python -m isort --check-only trendfy/
	venv/bin/python -m black --check trendfy/
	venv/bin/python -m pylint --rcfile=pyproject.toml trendfy/
	venv/bin/python -m mypy --config-file pyproject.toml trendfy/
	venv/bin/python -m flake8 trendfy/
	venv/bin/python -m flake8 *.md Makefile --select=W291
	venv/bin/python -m xenon trendfy/ -i */tests/ --max-absolute A --max-modules A --max-average A
	venv/bin/python -m xenon */tests/ --no-assert --max-absolute A --max-modules A --max-average A
	venv/bin/python -m bandit -q -r trendfy/ -x */tests/
	venv/bin/python -m bandit -s=B101 -q -r */tests/

test:
	venv/bin/python -m pytest -l -s -vvv --cov trendfy/ --cov-fail-under=90 --cov-report xml --cov-report term:skip-covered

all: check test

all-build: lint check test

req:
	@echo "Verifying requirements..."
	@while read line; do \
		if [[ "$$line" =~ ^[a-zA-Z0-9] ]]; then \
			echo "Checking package: $$line"; \
			pkg=$$line; \
			version=$$(grep "$$line" $(file) | sed 's/[^0-9.]/ /g' | cut -d " " -f 2); \
			echo $$pkg; \
			echo $$version; \
			# if [[ -z "$$version" ]]; then \
			# 	version=$$(pip show $$pkg | grep "^Version: " | cut -d " " -f 2); \
			# fi; \
			# echo "$$pkg==$$version" >> requirements.tmp; \
			# pip show $$pkg | grep "Requires: " | cut -d " " -f2- | tr ", " "\n" >> requirements.tmp; \
		fi; \
	done < $(file)
	# @mv requirements.tmp $(file)
