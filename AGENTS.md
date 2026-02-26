# AGENTS.md

This file provides guidance to the agent when working with code in this
repository.

## Commands

### Environment Setup

```bash
export APP_ENV=local              # Required for most commands
make venv                         # Create/update venv with uv (uses --group dev)
source .venv/bin/activate         # Activate venv
make dotenv                       # Generate .env.<env> from TOML config files
```

### Running the App

```bash
make up.local                     # Run locally (uvicorn via src/run.py)
make up                           # Docker Compose: detached
make up.echo                      # Docker Compose: foreground
make down                         # Stop containers
```

### Database (Supabase Local)

```bash
make up.db                        # Start Supabase local DB
make down.db                      # Stop DB
make reset.db                     # Reset DB to initial state
```

**Migration workflow** — `supabase/migrations/` is the canonical source of
truth. Every schema change needs a local `.sql` file. The correct order when
using the MCP tool:

1. Apply via `apply_migration` (MCP generates a timestamp automatically)
2. Call `list_migrations` to read back the assigned version number
3. Create `supabase/migrations/<version>_<name>.sql` with the same SQL

Never apply a migration via MCP without immediately writing the corresponding
file.

### Code Quality

```bash
make code.format                  # Format with ruff
make code.lint                    # Format + ruff check + slotscheck + mypy
make code.test                    # Run pytest (slow tests excluded by default)
make code.check                   # Lint + test
make code.cov                     # Coverage report (console)
```

### Running Tests

```bash
PYTHONPATH=src uv run pytest -v                                    # All tests (excludes @slow)
PYTHONPATH=src uv run pytest tests/app/unit/account/ -v            # One bounded context
PYTHONPATH=src uv run pytest tests/app/unit/account/application/sign_up/ -v  # One use case
PYTHONPATH=src uv run pytest -m slow -v                            # Only slow tests
PYTHONPATH=src uv run pytest -k "test_name" -v                     # Single test by name
```

## Architecture

**Stack:** Python 3.13, FastAPI, Dishka DI, SQLAlchemy 2.0 (imperative mapping),
bcrypt, PyJWT, PostgreSQL (Supabase)

**PYTHONPATH is `src/`** — all imports are relative to `src/`.

### Bounded Contexts

```
src/
├── account/          # Identity, auth, roles (Account aggregate)
│   ├── domain/       # Account entity, value objects, permissions, events
│   ├── application/  # Use cases: sign_up, log_in, activate_account, etc.
│   └── infrastructure/  # HTTP controllers, SQLAlchemy repos, JWT/bcrypt adapters
├── core/             # User profiles (Profile aggregate)
│   ├── domain/       # Profile entity, Username value object, events
│   ├── application/  # Use cases: set_username, get_my_profile, list_profiles
│   └── infrastructure/  # HTTP controllers, SQLAlchemy repos
└── shared/           # Cross-cutting kernel
    ├── domain/       # AggregateRoot, Entity, ValueObject, DomainEvent, authorization
    ├── application/  # EventDispatcher protocol
    └── infrastructure/  # App factory, DI providers, config loader, event registry
```

Each bounded context owns its own domain, application, and infrastructure
layers. Dependencies flow inward: `Infrastructure → Application → Domain`.

### Key Patterns

**Use case per directory** — each use case lives in `application/{use_case}/`
with:

- `command.py` (or `query.py`): input dataclass
- `port.py`: abstract Protocol (the use case interface)
- `handler.py`: concrete implementation

**AggregateRoot[T]** extends Entity with domain events (`_register_event()`,
`collect_events()`). Aggregates: `Account`, `Profile`.

**Domain events** connect bounded contexts. Example: `AccountCreated` event
triggers automatic `Profile` creation via `@handles(AccountCreated)` handler.

**Protocol-based repositories** — domain defines Protocols, infrastructure
implements them with SQLAlchemy imperative mapping (no ORM decorators).

**Permission framework** — `Permission[PC]` with `is_satisfied_by(context)`
pattern. Concrete: `CanManageSelf`, `CanManageSubordinate`, `CanManageRole`.

**UnitOfWork** — per-context (AccountUnitOfWork, CoreUnitOfWork) with
commit/rollback.

### DI Container (Dishka)

- Provider registry: `src/shared/infrastructure/config/di/provider_registry.py`
- Providers: `di/domain.py`, `di/application.py`, `di/infrastructure.py`,
  `di/settings.py`, `di/events.py`
- App factory: `src/shared/infrastructure/config/app_factory.py`
- Request-scoped dependencies (`Scope.REQUEST`)

### Configuration

- TOML files: `config/{env}/config.toml` + `config/{env}/.secrets.toml`
- Settings models: `src/shared/infrastructure/config/settings/`
- Loader resolves project root via `Path(__file__).resolve().parents[4]`
- Environments: `local`, `dev`, `prod` (set via `APP_ENV`)

### Event System

- `@handles(*event_types)` decorator registers event handlers
- Auto-discovered on startup via `auto_discover_handlers()`
- In-process async dispatch after UoW commit

## Conventions

- **Value objects**: frozen dataclasses with `slots=True`, validation in
  `__post_init__()`, raise `DomainTypeError`
- **Domain events**: frozen dataclasses extending `DomainEvent`, auto-generated
  `event_id` + `occurred_at`
- **HTTP controllers**: one router factory per feature, composed via
  `ErrorAwareRouter` from fastapi-error-map
- **Tests**: unit tests in `tests/app/unit/{context}/`, factories in
  `tests/app/unit/factories/`, mock with `create_autospec()`, async tests use
  `@pytest.mark.asyncio`
- **Linting**: ruff (format + lint), slotscheck, mypy (strict mode)
- **Line length**: 88 chars (ruff)

## Completion Checklist

At the end of each implementation:

1. If the change includes database/schema updates, verify a migration file was
   created in `supabase/migrations/`.
2. Run `make code.check` before considering the implementation complete.
