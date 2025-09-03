PY=python3
PIP=$(PY) -m pip

.PHONY: install lint fmt test

install:
	$(PIP) install -r requirements.txt

lint:
	ruff check .

fmt:
	black .

test:
	pytest -q

