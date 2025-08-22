.PHONY: setup lint format test run docker-build
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
lint:
	ruff check .
	black --check .
format:
	black .
test:
	pytest -q
run:
	python -m src.etl.run_all
docker-build:
	docker build -t etl-open-meteo:latest -f docker/Dockerfile .
