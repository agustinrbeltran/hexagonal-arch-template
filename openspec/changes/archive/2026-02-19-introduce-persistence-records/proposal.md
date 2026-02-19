## Why

SQLAlchemy's `map_imperatively()` currently maps directly to domain entities (aggregates). This couples the ORM hydration to domain value object construction, which fails when nullable composites are involved — specifically, `Username(None)` crashes during `__post_init__` validation when loading a `Profile` with no username set. More broadly, domain entities should not be constructed by the ORM; the ORM should map to plain persistence records, and a converter should handle `Record <-> Entity` translation.

## What Changes

- **BREAKING**: SQLAlchemy `map_imperatively()` will target new `Record` dataclasses (`AccountRecord`, `ProfileRecord`) instead of domain entities directly
- Introduce `Record` classes per aggregate — plain dataclasses with raw DB types (UUID, str, bool) and no domain validation
- Introduce `Converter` classes per aggregate — responsible for `Record -> Entity` and `Entity -> Record` translation, including value object wrapping/unwrapping
- Repository implementations change from `session.add(entity)` to `session.merge(converter.to_record(entity))`, and from returning entities directly to converting records via `converter.to_entity(record)`
- Remove all `composite()` usage from imperative mappings — records use raw column types
- Fixes the `TypeError: object of type 'NoneType' has no len()` bug when loading profiles with NULL username

## Capabilities

### New Capabilities

- `persistence-records`: Record dataclasses and converter classes that decouple SQLAlchemy ORM mapping from domain entities

### Modified Capabilities

- `infrastructure-adapters`: Imperative table mappings now target Record classes instead of domain entities; repositories use converters for Record <-> Entity translation; `composite()` is replaced by plain column mapping

## Impact

- `account/infrastructure/persistence/mappers/account.py` — maps to `AccountRecord` instead of `Account`
- `core/infrastructure/persistence/mappers/profile.py` — maps to `ProfileRecord` instead of `Profile`
- `account/infrastructure/persistence/sqla_account_repository.py` — queries `AccountRecord`, converts via `AccountConverter`
- `core/infrastructure/persistence/sqla_profile_repository.py` — queries `ProfileRecord`, converts via `ProfileConverter`
- `shared/infrastructure/config/app_factory.py` — `_map_tables()` unchanged (still calls same functions, but they now map records)
- Domain entities, repository protocols, use case handlers, and DI wiring remain unchanged
- RefreshToken is not an aggregate and keeps its current mapping
