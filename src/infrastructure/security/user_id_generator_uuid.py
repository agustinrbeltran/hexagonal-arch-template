import uuid_utils.compat as uuid_utils

from domain.user.ports import UserIdGenerator
from domain.user.value_objects import UserId


class UuidUserIdGenerator(UserIdGenerator):
    def generate(self) -> UserId:
        return UserId(uuid_utils.uuid7())
