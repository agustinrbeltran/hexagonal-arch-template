from common.domain.core.entities.base import Entity
from features.user.domain.core.enums.user_role import UserRole
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.core.vo.user_password_hash import UserPasswordHash
from features.user.domain.core.vo.username import Username


class User(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        role: UserRole,
        is_active: bool,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
