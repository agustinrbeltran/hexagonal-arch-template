# Environment
PYTHON := uv run python
CONFIGS_DIG := config
TOML_CONFIG_MANAGER := $(CONFIGS_DIG)/toml_config_manager.py

.PHONY: guard-APP_ENV env.local env dotenv venv venv.activate venv.deactivate help
guard-APP_ENV:
	@if [ -z "$$APP_ENV" ]; then \
		echo "APP_ENV is not set. Set APP_ENV before running this command."; \
		exit 1; \
	fi

env.local:
	@echo "Run: export APP_ENV=local"

env:
	@echo APP_ENV=$(APP_ENV)

dotenv: guard-APP_ENV
	@$(PYTHON) $(TOML_CONFIG_MANAGER) $(APP_ENV)

venv:
	@uv sync --group dev

venv.activate:
	@echo "Run: source .venv/bin/activate"

venv.deactivate:
	@echo "Run: deactivate"

help:
	@echo ""
	@echo "Environment:"
	@echo "  env.local      Print command to set APP_ENV=local in your shell"
	@echo "  env            Show current APP_ENV value"
	@echo "  dotenv         Generate .env.<env> from config files (requires APP_ENV)"
	@echo "  venv           Create/update the virtual environment with uv"
	@echo "  venv.activate  Print command to activate the venv"
	@echo "  venv.deactivate Print command to deactivate the venv"
	@echo ""
	@echo "App (docker compose):"
	@echo "  up             Start app containers in detached mode (requires APP_ENV)"
	@echo "  up.echo        Start app containers in foreground (requires APP_ENV)"
	@echo "  down           Stop app containers (requires APP_ENV)"
	@echo "  down.total     Stop app containers and remove volumes (requires APP_ENV)"
	@echo "  prune          Clean docker compose artifacts"
	@echo ""
	@echo "DB (Supabase local dev):"
	@echo "  up.db          Start Supabase local DB"
	@echo "  up.db-echo     Start Supabase local DB with debug output"
	@echo "  down.db        Stop Supabase local DB"
	@echo "  logs.db        Tail Supabase DB container logs"
	@echo "  shell.db       Open a shell inside the Supabase DB container"
	@echo ""
	@echo "Project structure:"
	@echo "  pycache-del    Remove __pycache__ directories"
	@echo "  tree           Show project tree after cleaning __pycache__"
	@echo "  plot-data      Plot Dishka dependency data"
	@echo ""
	@echo "Code quality:"
	@echo "  code.format    Format code with ruff"
	@echo "  code.lint      Lint with ruff, slotscheck, and mypy"
	@echo "  code.test      Run pytest"
	@echo "  code.cov       Run tests with coverage and print report"
	@echo "  code.cov.html  Run tests with coverage and generate HTML report"
	@echo "  code.check     Run lint and tests"

# App (docker compose)
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_PRUNE := scripts/makefile/docker_prune.sh

.PHONY: up up.echo down down.total prune
up: guard-APP_ENV
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up -d --build

up.echo: guard-APP_ENV
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up --build

down: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) down

down.total: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) down -v

prune:
	$(DOCKER_COMPOSE_PRUNE)

# DB (Supabase local dev)
SUPABASE := supabase
DOCKER := docker
SUPABASE_CONFIG := supabase/config.toml
SUPABASE_PROJECT_ID := $(shell python3 -c "import re, pathlib; p=pathlib.Path('$(SUPABASE_CONFIG)'); txt=p.read_text() if p.exists() else ''; m=re.search(r'^project_id\\s*=\\s*\\\"([^\\\"]+)\\\"', txt, re.M); print(m.group(1) if m else pathlib.Path().resolve().name)")
SUPABASE_DB_CONTAINER := supabase_db_$(SUPABASE_PROJECT_ID)

.PHONY: up.db up.db-echo down.db logs.db shell.db
up.db:
	@$(SUPABASE) start

up.db-echo:
	@$(SUPABASE) --debug start

down.db:
	@$(SUPABASE) stop

logs.db:
	@$(DOCKER) logs -f $(SUPABASE_DB_CONTAINER)

shell.db:
	@$(DOCKER) exec -it $(SUPABASE_DB_CONTAINER) sh

# Project structure visualization
PYCACHE_DEL := scripts/makefile/pycache_del.sh
DISHKA_PLOT_DATA := scripts/dishka/plot_dependencies_data.py

.PHONY: pycache-del tree plot-data
pycache-del:
	@$(PYCACHE_DEL)

# Clean tree
tree: pycache-del
	@tree

# Dishka
plot-data:
	@PYTHONPATH=src $(PYTHON) $(DISHKA_PLOT_DATA)

# Code quality
.PHONY: code.format code.lint code.test code.cov code.cov.html code.check
code.format:
	uv run ruff format

code.lint: code.format
	uv run ruff check --exit-non-zero-on-fix
	PYTHONPATH=src uv run slotscheck src
	uv run mypy

code.test:
	PYTHONPATH=src uv run pytest -v

code.cov:
	PYTHONPATH=src uv run coverage run -m pytest
	uv run coverage combine
	uv run coverage report

code.cov.html:
	PYTHONPATH=src uv run coverage run -m pytest
	uv run coverage combine
	uv run coverage html

code.check: code.lint code.test
