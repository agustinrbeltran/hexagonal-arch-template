from uuid import UUID

from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import Email
from account.infrastructure.persistence.mappers.account import AccountMetadataRecord
from shared.domain.account_id import AccountId


class AccountConverter:
    @staticmethod
    def to_entity(
        account_id: UUID,
        email: str,
        role: AccountRole,
        is_active: bool,
    ) -> Account:
        return Account(
            id_=AccountId(account_id),
            email=Email(email),
            role=role,
            is_active=is_active,
        )

    @staticmethod
    def to_record(entity: Account) -> AccountMetadataRecord:
        return AccountMetadataRecord(
            account_id=entity.id_.value,
            role=entity.role,
            is_active=entity.is_active,
        )
