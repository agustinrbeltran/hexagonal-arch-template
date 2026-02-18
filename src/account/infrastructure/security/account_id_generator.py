import uuid_utils.compat as uuid_utils

from account.domain.account.ports import AccountIdGenerator
from shared.domain.account_id import AccountId


class UuidAccountIdGenerator(AccountIdGenerator):
    def generate(self) -> AccountId:
        return AccountId(uuid_utils.uuid7())
