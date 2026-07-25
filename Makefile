PYTHON ?= python3
ENV = PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1

.PHONY: demo test lint serve reproduce-flawedbench reproduce-grader-rates

demo:
	$(ENV) $(PYTHON) -m sieve demo --output docs/demo/report.html --json-output docs/demo/audit.json --db work/findings.sqlite

test:
	$(ENV) $(PYTHON) -m unittest discover -s tests -v

lint:
	$(ENV) $(PYTHON) scripts/lint.py

serve:
	$(ENV) $(PYTHON) -m sieve serve

reproduce-flawedbench:
	$(ENV) $(PYTHON) -m sieve audit flawedbench --budget 200 --output docs/demo/report.html --json-output docs/demo/audit.json

reproduce-grader-rates:
	$(ENV) $(PYTHON) -m sieve audit flawedbench --budget 200 --json-output docs/demo/grader-rates.json
