CONFIG ?= examples/config_test.yaml

.PHONY: run test

run:
	python3 src/main.py $(CONFIG)

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
