## 1. Account Record and Converter

- [x] 1.1 Add `AccountRecord` dataclass to `account/infrastructure/persistence/mappers/account.py` with raw DB types (`id: UUID`, `email: str`, `password_hash: bytes`, `role: AccountRole`, `is_active: bool`)
- [x] 1.2 Update `map_accounts_table()` to map `AccountRecord` instead of `Account` — remove `composite()`, `column_prefix`, and `exclude_properties`
- [x] 1.3 Create `account/infrastructure/persistence/converters/__init__.py`
- [x] 1.4 Create `AccountConverter` at `account/infrastructure/persistence/converters/account_converter.py` with `to_entity(record) -> Account` and `to_record(entity) -> AccountRecord`

## 2. Profile Record and Converter

- [x] 2.1 Add `ProfileRecord` dataclass to `core/infrastructure/persistence/mappers/profile.py` with raw DB types (`id: UUID`, `account_id: UUID`, `username: str | None`)
- [x] 2.2 Update `map_profiles_table()` to map `ProfileRecord` instead of `Profile` — remove `composite()`, `column_prefix`, and `exclude_properties`
- [x] 2.3 Create `core/infrastructure/persistence/converters/__init__.py`
- [x] 2.4 Create `ProfileConverter` at `core/infrastructure/persistence/converters/profile_converter.py` with `to_entity(record) -> Profile` and `to_record(entity) -> ProfileRecord` — handle `username: None` gracefully

## 3. Update Account Repository

- [x] 3.1 Update `SqlaAccountRepository.save()` to convert `Account` to `AccountRecord` via `AccountConverter` and use `session.merge(record)`
- [x] 3.2 Update `SqlaAccountRepository.get_by_id()` to query `AccountRecord`, convert to `Account` via `AccountConverter`
- [x] 3.3 Update `SqlaAccountRepository.get_by_email()` to query `AccountRecord` with raw email string, convert to `Account` via `AccountConverter`
- [x] 3.4 Update `SqlaAccountRepository.get_all()` — this already queries raw columns for `AccountQueryModel`, verify it still works with `AccountRecord` as the mapped class

## 4. Update Profile Repository

- [x] 4.1 Update `SqlaProfileRepository.save()` to convert `Profile` to `ProfileRecord` via `ProfileConverter` and use `session.merge(record)`
- [x] 4.2 Update `SqlaProfileRepository.get_by_id()` to query `ProfileRecord`, convert to `Profile` via `ProfileConverter`
- [x] 4.3 Update `SqlaProfileRepository.get_by_account_id()` to query `ProfileRecord` with raw UUID, convert to `Profile` via `ProfileConverter`
- [x] 4.4 Update `SqlaProfileRepository.get_all()` — verify it still works with `ProfileRecord` as the mapped class

## 5. Update Tests

- [x] 5.1 Update unit test factories and mocks that reference `Account` or `Profile` as ORM-mapped classes — ensure tests construct entities via domain constructors, not ORM loading
- [x] 5.2 Run full test suite (`make code.test`) and fix any failures
- [x] 5.3 Run linting (`make code.lint`) and fix any issues
