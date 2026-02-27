## ADDED Requirements

### Requirement: SqlaAccountRepository save persists converted record
The `SqlaAccountRepository.save()` method SHALL convert an `Account` entity to an `AccountMetadataRecord` and merge it into the session.

#### Scenario: Save calls session merge with converted record
- **WHEN** `save()` is called with an `Account` entity
- **THEN** the session's `merge` method is called once with an `AccountMetadataRecord` whose `account_id`, `role`, and `is_active` match the entity

#### Scenario: Save wraps SQLAlchemy errors in DataMapperError
- **WHEN** `save()` is called and the session raises `SQLAlchemyError`
- **THEN** a `DataMapperError` is raised

### Requirement: SqlaAccountRepository get_by_id retrieves by primary key
The `SqlaAccountRepository.get_by_id()` method SHALL query by account ID and return an `Account` entity or `None`.

#### Scenario: Account found
- **WHEN** `get_by_id()` is called with an existing account ID
- **THEN** an `Account` entity is returned with matching fields

#### Scenario: Account not found
- **WHEN** `get_by_id()` is called with a non-existent account ID
- **THEN** `None` is returned

#### Scenario: For-update locking
- **WHEN** `get_by_id()` is called with `for_update=True`
- **THEN** the query includes `WITH FOR UPDATE` clause

#### Scenario: Database error wrapped
- **WHEN** the session raises `SQLAlchemyError`
- **THEN** a `DataMapperError` is raised

### Requirement: SqlaAccountRepository get_by_email retrieves by email
The `SqlaAccountRepository.get_by_email()` method SHALL query by email and return an `Account` entity or `None`.

#### Scenario: Account found by email
- **WHEN** `get_by_email()` is called with an existing email
- **THEN** an `Account` entity is returned with matching fields

#### Scenario: Account not found by email
- **WHEN** `get_by_email()` is called with a non-existent email
- **THEN** `None` is returned

### Requirement: SqlaAccountRepository get_all returns paginated results
The `SqlaAccountRepository.get_all()` method SHALL return a paginated, sorted list of accounts.

#### Scenario: Returns accounts with total count
- **WHEN** `get_all()` is called with valid pagination and sorting params
- **THEN** a `ListAccountsQM` is returned with `accounts` list and `total` count

#### Scenario: Invalid sorting field
- **WHEN** `get_all()` is called with an unsupported sorting field
- **THEN** a `SortingError` is raised

### Requirement: SqlaAccountUnitOfWork commit flushes and commits
The `SqlaAccountUnitOfWork.commit()` method SHALL flush then commit the session.

#### Scenario: Successful commit
- **WHEN** `commit()` is called
- **THEN** the session's `flush` and `commit` methods are called in order

#### Scenario: Integrity error on flush
- **WHEN** `flush()` raises `IntegrityError`
- **THEN** a `DataMapperError` with constraint violation message is raised

#### Scenario: SQLAlchemy error on commit
- **WHEN** `commit()` raises `SQLAlchemyError`
- **THEN** a `DataMapperError` is raised

### Requirement: SqlaAccountUnitOfWork rollback delegates to session
The `SqlaAccountUnitOfWork.rollback()` method SHALL call the session's `rollback`.

#### Scenario: Rollback delegates
- **WHEN** `rollback()` is called
- **THEN** the session's `rollback` method is called once
