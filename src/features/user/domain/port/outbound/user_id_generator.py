from abc import abstractmethod

from features.user.domain.core.vo.user_id import UserId


class UserIdGenerator:
    @abstractmethod
    def generate(self) -> UserId: ...
