setup: first_run create_venv install_alembic run_migrations

up:
	docker-compose -f docker-compose.yml up --build

first_run:
	docker-compose -f docker-compose.yml up --build -d

create_venv:
	python3 -m venv .venv
	@echo "Virtual environment created."

install_alembic:
	. .venv/bin/activate; pip install alembic psycopg2-binary python-dotenv
	@echo "Alembic and psycopg2 installed in the virtual environment."

run_migrations:
	. .venv/bin/activate; sleep 5; export DB_HOST=localhost; alembic upgrade head
	@echo "Alembic migrations applied."
