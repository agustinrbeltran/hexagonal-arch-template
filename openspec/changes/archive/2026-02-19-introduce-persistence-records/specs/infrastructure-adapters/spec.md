## MODIFIED Requirements

### Requirement: Imperative table mappings per context
- **WHEN** inspecting `account/infrastructure/persistence/mappers/`
- **THEN** it contains the SQLAlchemy `Table` definition for `accounts`, the `AccountRecord` dataclass, and `map_imperatively()` mapping `AccountRecord` to the table without `composite()`, `column_prefix`, or `exclude_properties`
- **WHEN** inspecting `core/infrastructure/persistence/mappers/`
- **THEN** it contains the SQLAlchemy `Table` definition for `profiles`, the `ProfileRecord` dataclass, and `map_imperatively()` mapping `ProfileRecord` to the table without `composite()`, `column_prefix`, or `exclude_properties`

#### Scenario: Account table maps to AccountRecord
- **WHEN** `map_accounts_table()` is called
- **THEN** `AccountRecord` is mapped imperatively to `accounts_table` with direct column-to-attribute mapping

#### Scenario: Profile table maps to ProfileRecord
- **WHEN** `map_profiles_table()` is called
- **THEN** `ProfileRecord` is mapped imperatively to `profiles_table` with direct column-to-attribute mapping

### Requirement: Accounts table mapper
The system SHALL provide an imperative SQLAlchemy mapper at `account/infrastructure/persistence/mappers/account.py` mapping `AccountRecord` to the `accounts` table. It SHALL NOT use `composite()` — all columns map directly to `AccountRecord` attributes with matching names.

#### Scenario: Account mapper uses direct column mapping
- **WHEN** the mapper registry is initialized
- **THEN** `AccountRecord.id` maps to `accounts.id`, `AccountRecord.email` maps to `accounts.email`, `AccountRecord.password_hash` maps to `accounts.password_hash`

### Requirement: Profiles table mapper
The system SHALL provide an imperative SQLAlchemy mapper at `core/infrastructure/persistence/mappers/profile.py` mapping `ProfileRecord` to the `profiles` table. It SHALL NOT use `composite()` — all columns map directly to `ProfileRecord` attributes with matching names.

#### Scenario: Profile mapper uses direct column mapping
- **WHEN** the mapper registry is initialized
- **THEN** `ProfileRecord.id` maps to `profiles.id`, `ProfileRecord.account_id` maps to `profiles.account_id`, `ProfileRecord.username` maps to `profiles.username`

### Requirement: Persistence adapters organized by bounded context
The system SHALL place SQLAlchemy repository implementations, table mappers, and converters under each bounded context's `infrastructure/persistence/` directory.

Account BC: `account/infrastructure/persistence/` with `SqlaAccountRepository`, account table mapper, `AccountRecord`, and `AccountConverter`.
Core BC: `core/infrastructure/persistence/` with `SqlaProfileRepository`, profile table mapper, `ProfileRecord`, and `ProfileConverter`.
Shared: Refresh token persistence stays under `account/infrastructure/` since it's Account BC infrastructure.

#### Scenario: SQLAlchemy repository implements domain port
- **WHEN** `SqlaAccountRepository` is defined in `account/infrastructure/persistence/`
- **THEN** it implements the `AccountRepository` protocol from `account/domain/account/repository.py`
- **AND** it queries `AccountRecord` and converts to `Account` via `AccountConverter`

#### Scenario: SqlaProfileRepository implements domain port
- **WHEN** `SqlaProfileRepository` is defined in `core/infrastructure/persistence/`
- **THEN** it implements the `ProfileRepository` protocol from `core/domain/profile/repository.py`
- **AND** it queries `ProfileRecord` and converts to `Profile` via `ProfileConverter`

#### Scenario: Repository save uses merge
- **WHEN** `save(entity)` is called on a repository
- **THEN** it converts the entity to a record via the converter and calls `session.merge(record)`

#### Scenario: Repository get converts record to entity
- **WHEN** `get_by_id(id)` is called on a repository
- **THEN** it queries for the record, and if found, converts it to a domain entity via the converter
