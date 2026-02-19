## ADDED Requirements

### Requirement: AccountRecord persistence model
The system SHALL provide an `AccountRecord` dataclass at `account/infrastructure/persistence/mappers/account.py` with plain database types: `id: UUID`, `email: str`, `password_hash: bytes`, `role: AccountRole`, `is_active: bool`. It SHALL be the target of `map_imperatively()` instead of the `Account` domain entity.

#### Scenario: AccountRecord has raw database types
- **WHEN** inspecting `AccountRecord`
- **THEN** all attributes are raw types (`UUID`, `str`, `bytes`, `AccountRole`, `bool`) with no domain value objects

#### Scenario: AccountRecord is the ORM mapping target
- **WHEN** `map_accounts_table()` is called
- **THEN** `mapper_registry.map_imperatively()` maps `AccountRecord` to `accounts_table`

### Requirement: ProfileRecord persistence model
The system SHALL provide a `ProfileRecord` dataclass at `core/infrastructure/persistence/mappers/profile.py` with plain database types: `id: UUID`, `account_id: UUID`, `username: str | None`. It SHALL be the target of `map_imperatively()` instead of the `Profile` domain entity.

#### Scenario: ProfileRecord has raw database types
- **WHEN** inspecting `ProfileRecord`
- **THEN** all attributes are raw types (`UUID`, `str | None`) with no domain value objects

#### Scenario: ProfileRecord is the ORM mapping target
- **WHEN** `map_profiles_table()` is called
- **THEN** `mapper_registry.map_imperatively()` maps `ProfileRecord` to `profiles_table`

#### Scenario: ProfileRecord handles NULL username
- **WHEN** a profile row has `username IS NULL` in the database
- **THEN** `ProfileRecord.username` is `None` without any validation error

### Requirement: AccountConverter translates between record and entity
The system SHALL provide an `AccountConverter` class at `account/infrastructure/persistence/converters/account_converter.py` with two static methods: `to_entity(record: AccountRecord) -> Account` and `to_record(entity: Account) -> AccountRecord`.

#### Scenario: AccountConverter creates entity from record
- **WHEN** `AccountConverter.to_entity(record)` is called with a valid `AccountRecord`
- **THEN** it returns an `Account` entity with value objects constructed from raw values (`AccountId`, `Email`, `AccountPasswordHash`)

#### Scenario: AccountConverter creates record from entity
- **WHEN** `AccountConverter.to_record(entity)` is called with an `Account` entity
- **THEN** it returns an `AccountRecord` with raw values extracted from value objects (`.value`)

### Requirement: ProfileConverter translates between record and entity
The system SHALL provide a `ProfileConverter` class at `core/infrastructure/persistence/converters/profile_converter.py` with two static methods: `to_entity(record: ProfileRecord) -> Profile` and `to_record(entity: Profile) -> ProfileRecord`.

#### Scenario: ProfileConverter creates entity from record with username
- **WHEN** `ProfileConverter.to_entity(record)` is called with a `ProfileRecord` where `username` is not None
- **THEN** it returns a `Profile` entity with `username` set to `Username(record.username)`

#### Scenario: ProfileConverter creates entity from record without username
- **WHEN** `ProfileConverter.to_entity(record)` is called with a `ProfileRecord` where `username` is None
- **THEN** it returns a `Profile` entity with `username` set to `None`

#### Scenario: ProfileConverter creates record from entity without username
- **WHEN** `ProfileConverter.to_record(entity)` is called with a `Profile` entity where `username` is None
- **THEN** it returns a `ProfileRecord` with `username` set to `None`
