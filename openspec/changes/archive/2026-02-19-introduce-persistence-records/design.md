## Context

SQLAlchemy's imperative mapping (`map_imperatively()`) currently targets domain entities directly. The ORM hydrates `Account` and `Profile` aggregates, using `composite()` to construct value objects from raw column values. This creates a tight coupling: SQLAlchemy must know how to construct domain VOs, and domain VOs must tolerate whatever the ORM feeds them — including `None` for nullable columns.

The immediate trigger is a `TypeError` when loading a `Profile` with a NULL `username` column: SQLAlchemy calls `Username(None)`, which crashes in `__post_init__` validation. But the root issue is architectural — the ORM should not be constructing domain objects at all.

Current flow:
```
DB Row → map_imperatively(Entity) → composite(VO, column) → Entity with VOs
```

## Goals / Non-Goals

**Goals:**
- Decouple SQLAlchemy ORM mapping from domain entity construction
- Introduce Record classes as the ORM's mapping target (plain dataclasses, raw types)
- Introduce Converter classes to handle Record <-> Entity translation
- Fix the nullable `Username` composite crash
- Apply the pattern consistently to both aggregates (`Account`, `Profile`)

**Non-Goals:**
- Changing the domain entities, value objects, or repository protocols
- Refactoring `RefreshToken` (not an aggregate, already a plain dataclass)
- Changing the UnitOfWork implementations (they still operate on the same session)
- Introducing a generic/abstract record or converter base class (keep it simple per aggregate)

## Decisions

### Decision 1: Record classes are plain dataclasses with raw DB types

Records use `UUID`, `str`, `bytes`, `bool`, enums — no domain value objects. They live alongside the table definition in the existing mapper file (e.g., `account/infrastructure/persistence/mappers/account.py`).

```python
@dataclass(eq=False, kw_only=True)
class AccountRecord:
    id: UUID
    email: str
    password_hash: bytes
    role: AccountRole
    is_active: bool
```

**Rationale**: Keeping Record + Table in the same file is natural — they represent the same persistence concern. The Record is the Python representation of the table row.

**Alternative considered**: Separate `account_record.py` file. Rejected because it adds file count without adding clarity — the record and table definition are tightly coupled.

### Decision 2: Converters live in a `converters/` directory per context

Each aggregate gets a converter at `{context}/infrastructure/persistence/converters/{aggregate}_converter.py`.

```python
class AccountConverter:
    @staticmethod
    def to_entity(record: AccountRecord) -> Account:
        return Account(
            id_=AccountId(record.id),
            email=Email(record.email),
            password_hash=AccountPasswordHash(record.password_hash),
            role=record.role,
            is_active=record.is_active,
        )

    @staticmethod
    def to_record(entity: Account) -> AccountRecord:
        return AccountRecord(
            id=entity.id_.value,
            email=entity.email.value,
            password_hash=entity.password_hash.value,
            role=entity.role,
            is_active=entity.is_active,
        )
```

**Rationale**: Converters are a distinct concern from table definition and repository queries. A separate `converters/` directory makes this explicit and follows the existing pattern of organizing by concern within `persistence/`.

**Alternative considered**: Putting conversion logic inside the repository. Rejected because it mixes query logic with mapping logic and duplicates conversion code across repository methods.

### Decision 3: Use `session.merge()` for the save path

Repositories use `session.merge(record)` for both insert and update, replacing `session.add(entity)`.

```python
def save(self, account: Account) -> None:
    record = AccountConverter.to_record(account)
    self._session.merge(record)
```

**Rationale**: `merge()` handles both insert (new PK) and update (existing PK) transparently. This aligns with the repository pattern where `save` is the single persistence method — existence checks belong in the domain/application layer, not the repository.

**Trade-off**: `merge()` performs a SELECT to check if the record exists before INSERT/UPDATE. This is an extra round-trip per save. Acceptable for this codebase's scale.

### Decision 4: Repository queries use raw types in WHERE clauses

Instead of `Account.id_ == account_id` (which relied on composite comparators), queries use raw types:

```python
stmt = select(AccountRecord).where(AccountRecord.id == account_id.value)
```

**Rationale**: Without `composite()`, there are no composite comparators. Using `.value` to unwrap VOs in queries is explicit and simple. The VO → raw conversion is a one-liner at the query boundary.

### Decision 5: Remove all `composite()` usage from imperative mappings

Records map columns directly — no `composite()`, no `column_prefix`, no `exclude_properties`.

```python
def map_accounts_table() -> None:
    mapper_registry.map_imperatively(AccountRecord, accounts_table)
```

**Rationale**: When the mapped class has attribute names matching column names, SQLAlchemy maps them automatically. No `properties` dict needed. No `column_prefix` needed (that was only needed to avoid clashing with entity attributes like `id_`).

## Risks / Trade-offs

- **Extra SELECT on save** → `merge()` checks for existing records. Acceptable at current scale; can be optimized later if needed.
- **Record/Entity construction on every read** → Each `get_by_*` now constructs a Record (via ORM) then an Entity (via Converter). The overhead is negligible for single-entity reads.
- **Stale events on load** → Domain entities constructed by the Converter always start with empty `_events`. This is correct — persisted entities should not carry stale events. Events are only accumulated during the current request lifecycle.
- **`get_all` queries remain unchanged** → The list/query methods already use raw column queries returning `TypedDict` query models, not entities. No conversion needed there.
