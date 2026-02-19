from account.domain.account.entity import Account
from account.domain.account.value_objects import AccountPasswordHash, Email
from account.infrastructure.persistence.mappers.account import AccountRecord
from shared.domain.account_id import AccountId


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
