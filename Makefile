PYTHON ?= python3
ENV = PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1

.PHONY: demo test lint reproduce-flawedbench reproduce-grader-rates

demo:
	$(ENV) $(PYTHON) -m sieve demo --output docs/demo/index.html --json-output docs/demo/audit.json --db work/findings.sqlite

test:
	$(ENV) $(PYTHON) -m unittest discover -s tests -v

lint:
	$(ENV) $(PYTHON) scripts/lint.py

reproduce-flawedbench:
	$(ENV) $(PYTHON) -m sieve audit flawedbench --budget 200 --output docs/demo/index.html --json-output docs/demo/audit.json

reproduce-grader-rates:
	$(ENV) $(PYTHON) -m sieve audit flawedbench --budget 200 --json-output docs/demo/grader-rates.json

