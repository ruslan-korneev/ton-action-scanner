all: fmt lint check-migrations test

fmt:
	poetry run black src
	poetry run isort src

lint:
	poetry run ruff check .
	poetry run mypy .
	poetry run poetry check
	poetry run dotenv-linter .env.example

check-migrations:
	poetry run alembic check

test:
	poetry run pytest --numprocesses logical --dist worksteal
	poetry run coverage-threshold
