# CLAUDE.md

## Project Overview

This is a **hexagonal architecture (ports and adapters) template** built with FastAPI, Python 3.13, and SQLAlchemy. It demonstrates feature-based bounded contexts with CQRS principles and Domain-Driven Design. The application provides user account management (signup, login, logout, password change) and user administration (CRUD, role assignment, soft-delete).

## Quick Reference

```bash
# Install dependencies
uv sync --group dev

# Run all code quality checks (format + lint + test)
make code.check

# Individual checks
make code.format          # ruff format
make code.lint            # ruff format + ruff check + slotscheck + mypy
make code.test            # PYTHONPATH=src uv run pytest -v

# Run tests with coverage
make code.cov

# Start local database (Supabase)
make up.db

# Start app (requires APP_ENV and running DB)
export APP_ENV=local
make dotenv
make up
```

## Architecture

### Hexagonal Architecture (Ports and Adapters)

Each feature is a self-contained hexagon organized as:

```
src/features/<feature>/
├── domain/
│   ├── core/          # Entities, value objects, enums, services, exceptions
│   └── port/
│       ├── inbound/   # Use case interfaces (what domain offers)
│       └── outbound/  # Gateway interfaces (what domain needs)
├── adapter/           # Concrete implementations of outbound ports
└── entrypoint/
    └── rest/          # Controllers and routers (driving adapters)
```

**Dependency rule**: Dependencies always point inward. Domain core depends only on port abstractions. Adapters implement outbound ports. Entrypoints call inbound ports.

### Features (Bounded Contexts)

- **`account`** - Authentication: signup, login, logout, password change
- **`user`** - User administration: CRUD, role management, activation/deactivation

### Shared Code

- **`src/common/`** - Cross-cutting concerns: base entity/value object classes, shared ports (Flusher, TransactionManager), persistence utilities, REST error handling

### Application Setup

- **`src/setup/config/`** - Settings models (Pydantic), environment loader
- **`src/setup/ioc/`** - Dishka dependency injection container and providers
- **`src/setup/app_factory.py`** - FastAPI app creation with middleware and DI wiring
- **`src/run.py`** - Entry point (`make_app` factory function)

## Key Conventions

### Domain Modeling

- **Entities** have identity (`id_` field), are mutable, and compared by identity
- **Value Objects** are immutable dataclasses with validation in `__post_init__`, compared by value
- **Domain Services** implement inbound port use case interfaces and orchestrate domain logic
- **Outbound Ports** are `Protocol` classes defining infrastructure needs

### CQRS

- **Commands** are write operations (e.g., `CreateUserCommand`, `LogInCommand`)
- **Queries** are read operations (e.g., `ListUsersQuery`) with separate query models

### Dependency Injection

Uses **Dishka** (not FastAPI's `Depends`) for framework-agnostic DI:

- `APP` scope: singletons initialized once per application lifetime
- `REQUEST` scope: created/destroyed per HTTP request
- Providers are registered in `src/setup/ioc/provider_registry.py`
- Controllers use `@inject` decorator with `FromDishka[T]` type annotations

### Naming Conventions

- Adapter files: `<impl>_<port_name>_adapter.py` (e.g., `sqla_user_repository_adapter_.py`)
- Use case ports: `<action>_<entity>_use_case.py` (e.g., `create_user_use_case.py`)
- Value objects directory: `vo/`
- Entity `id` field is named `id_` (trailing underscore to avoid shadowing builtin)

### Imports

- Source root is `src/` (set via `PYTHONPATH=src`)
- Imports are absolute from `src/` (e.g., `from features.user.domain.core.entities.user import User`)
- isort managed by ruff with `combine-as-imports = true` and `force-wrap-aliases = true`

## Code Quality Tools

All configured in `pyproject.toml`:

| Tool | Purpose | Config Key |
|------|---------|------------|
| **ruff** (0.12.5) | Formatter + linter | `[tool.ruff]` |
| **mypy** (1.17.0) | Type checking (strict mode) | `[tool.mypy]` |
| **slotscheck** (0.19.1) | Validates `__slots__` usage | `[tool.slotscheck]` |
| **pytest** (8.4.1) | Testing | `[tool.pytest.ini_options]` |
| **coverage** (7.10.0) | Code coverage | `[tool.coverage]` |

### Ruff Rules

40+ rule sets enabled including flake8-bugbear, pylint, bandit (security), isort, pyupgrade. Line length is 88. Preview mode is enabled.

### Mypy

Strict mode with `sqlalchemy.ext.mypy.plugin` and `pydantic.mypy` plugins. `ignore_missing_imports = true` and `allow_subclassing_any = true` are set.

### Pre-commit

Single hook runs `make code.check` (format + lint + test) on every commit.

## Testing

```
tests/
├── app/
│   ├── unit/           # Domain logic tests (services, value objects, enums)
│   ├── integration/    # Config loader, infrastructure tests
│   └── performance/    # Profiling scripts (bcrypt work factor)
```

- Tests marked `@pytest.mark.slow` are excluded by default (`addopts = "-m 'not slow'"`)
- Async tests use `pytest-asyncio` with function-scoped event loops
- Run: `PYTHONPATH=src uv run pytest -v`

## Technology Stack

- **Python** 3.13 (pinned: `==3.13.*`)
- **FastAPI** 0.121.0 with **uvicorn** + **uvloop**
- **SQLAlchemy** 2.0.44 (async, PostgreSQL via psycopg)
- **Dishka** 1.7.2 (dependency injection)
- **bcrypt** 5.0.0 (password hashing)
- **PyJWT** 2.10.1 (JWT authentication)
- **orjson** 3.11.4 (fast JSON responses)
- **uv** (package manager, lockfile: `uv.lock`)

## Project Structure

```
hexagonal-arch-template/
├── .github/workflows/ci.yaml    # CI pipeline
├── config/                       # Environment configs (local/dev/prod)
│   ├── local/                    # Docker Compose, .env, config.toml
│   └── toml_config_manager.py   # Generates .env from TOML config
├── docs/                         # Architecture diagrams (SVG)
├── scripts/                      # Makefile helpers, DI graph plotting
├── src/
│   ├── run.py                    # App entry point
│   ├── common/                   # Shared building blocks
│   ├── features/
│   │   ├── account/              # Auth bounded context
│   │   └── user/                 # User management bounded context
│   └── setup/                    # Config, DI, app factory
├── supabase/                     # Supabase local dev config
├── tests/                        # Unit, integration, performance tests
├── Makefile                      # Development commands
└── pyproject.toml                # Project metadata and tool config
```

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/account/signup` - Register user
- `POST /api/v1/account/login` - Authenticate
- `PUT /api/v1/account/password` - Change own password
- `DELETE /api/v1/account/logout` - End session
- `POST /api/v1/users/` - Create user (admin)
- `GET /api/v1/users/` - List users (admin)
- `PUT /api/v1/users/{id}/password` - Set user password (admin)
- `PUT /api/v1/users/{id}/roles/admin` - Grant admin (super-admin)
- `DELETE /api/v1/users/{id}/roles/admin` - Revoke admin (super-admin)
- `PUT /api/v1/users/{id}/activation` - Activate user (admin)
- `DELETE /api/v1/users/{id}/activation` - Deactivate user (admin)

## CI/CD

GitHub Actions (`.github/workflows/ci.yaml`) runs on push and pull request:
1. Install Python 3.13 + uv
2. `uv sync --locked --group dev`
3. `make code.check` (format, lint, type check, test)
4. Docker Compose build + health check + signup test

## Development Workflow

1. Ensure Python 3.13 and `uv` are installed
2. `uv sync --group dev` to install dependencies
3. Make changes following the hexagonal architecture patterns
4. `make code.check` before committing (also runs as pre-commit hook)
5. Format issues are auto-fixed by `ruff format`; lint issues must be resolved manually
