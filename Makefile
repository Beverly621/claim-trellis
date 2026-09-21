.PHONY: install test lint typecheck check run

install:
	python3 -m pip install -e '.[dev]'

test:
	pytest --cov=claim_trellis --cov-report=term-missing

lint:
	ruff check .

typecheck:
	mypy

check: lint typecheck test

run:
	claim-trellis serve
