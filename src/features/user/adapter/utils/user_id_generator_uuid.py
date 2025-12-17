import uuid_utils.compat as uuid_utils

from features.user.domain.core.vo.user_id import UserId
from features.user.domain.port.outbound.user_id_generator import UserIdGenerator


class UuidUserIdGenerator(UserIdGenerator):
    def generate(self) -> UserId:
        return UserId(uuid_utils.uuid7())
