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

# Environment
PYTHON := uv run python
CONFIGS_DIG := config
TOML_CONFIG_MANAGER := $(CONFIGS_DIG)/toml_config_manager.py

.PHONY: guard-APP_ENV
guard-APP_ENV:
	@if [ -z "$$APP_ENV" ]; then \
		echo "APP_ENV is not set. Set APP_ENV before running this command."; \
		exit 1; \
	fi

.PHONY: env dotenv
env:
	@echo APP_ENV=$(APP_ENV)

dotenv: guard-APP_ENV
	@$(PYTHON) $(TOML_CONFIG_MANAGER) $(APP_ENV)

# Docker compose (app)
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PRUNE := scripts/makefile/docker_prune.sh

# Supabase (local dev) DB
SUPABASE := supabase
DOCKER := docker
SUPABASE_CONFIG := supabase/config.toml
SUPABASE_PROJECT_ID := $(shell python3 -c "import re, pathlib; p=pathlib.Path('$(SUPABASE_CONFIG)'); txt=p.read_text() if p.exists() else ''; m=re.search(r'^project_id\\s*=\\s*\\\"([^\\\"]+)\\\"', txt, re.M); print(m.group(1) if m else pathlib.Path().resolve().name)")
SUPABASE_DB_CONTAINER := supabase_db_$(SUPABASE_PROJECT_ID)

.PHONY: up.db up.db-echo up up.echo down down.total logs.db shell.db prune
up.db:
	@$(SUPABASE) start

up.db-echo:
	@$(SUPABASE) --debug start

up: guard-APP_ENV dotenv
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && \
		if [ -f .env.$(APP_ENV) ]; then \
			set -a; \
			. ./.env.$(APP_ENV); \
			set +a; \
		fi && \
		DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 $(DOCKER_COMPOSE) up -d --build

up.echo: guard-APP_ENV dotenv
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && \
		if [ -f .env.$(APP_ENV) ]; then \
			set -a; \
			. ./.env.$(APP_ENV); \
			set +a; \
		fi && \
		DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 $(DOCKER_COMPOSE) up --build

down.db:
	@$(SUPABASE) stop

down: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && \
		if [ -f .env.$(APP_ENV) ]; then \
			set -a; \
			. ./.env.$(APP_ENV); \
			set +a; \
		fi && \
		$(DOCKER_COMPOSE) down

down.total: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && \
		if [ -f .env.$(APP_ENV) ]; then \
			set -a; \
			. ./.env.$(APP_ENV); \
			set +a; \
		fi && \
		$(DOCKER_COMPOSE) down -v

logs.db:
	@$(DOCKER) logs -f $(SUPABASE_DB_CONTAINER)

shell.db:
	@$(DOCKER) exec -it $(SUPABASE_DB_CONTAINER) sh

prune:
	$(DOCKER_COMPOSE_PRUNE)

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
