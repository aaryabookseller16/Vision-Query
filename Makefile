.PHONY: check demo stop

check:
	cd frontend && npm ci && npm run lint && npm test && npm run build && npm audit --omit=dev
	python3 -m venv backend/.venv-test
	backend/.venv-test/bin/pip install -q -r backend/requirements-test.txt
	cd backend && PYTHONPATH=. .venv-test/bin/pytest -q
	docker compose config --quiet

demo:
	docker compose up --build

stop:
	docker compose down
