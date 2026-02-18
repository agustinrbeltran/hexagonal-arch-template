from abc import abstractmethod

from core.domain.profile.value_objects import ProfileId


class ProfileIdGenerator:
    @abstractmethod
    def generate(self) -> ProfileId: ...
