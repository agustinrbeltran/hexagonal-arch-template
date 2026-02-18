import uuid_utils.compat as uuid_utils

from core.domain.profile.ports import ProfileIdGenerator
from core.domain.profile.value_objects import ProfileId


class UuidProfileIdGenerator(ProfileIdGenerator):
    def generate(self) -> ProfileId:
        return ProfileId(uuid_utils.uuid7())
