from typing import TypedDict
from uuid import UUID

from features.user.domain.core.enums.user_role import UserRole


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool


class ListUsersQM(TypedDict):
    users: list[UserQueryModel]
    total: int
