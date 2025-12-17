from sqlalchemy import UUID, Boolean, Column, Enum, LargeBinary, String, Table
from sqlalchemy.orm import composite

from common.adapter.persistence_sqla.registry import mapper_registry
from features.user.domain.core.entities.user import User
from features.user.domain.core.enums.user_role import UserRole
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.core.vo.user_password_hash import UserPasswordHash
from features.user.domain.core.vo.username import Username

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "role",
        Enum(UserRole, name="userrole"),
        default=UserRole.USER,
        nullable=False,
    ),
    Column("is_active", Boolean, default=True, nullable=False),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "id_": composite(UserId, users_table.c.id),
            "username": composite(Username, users_table.c.username),
            "password_hash": composite(UserPasswordHash, users_table.c.password_hash),
            "role": users_table.c.role,
            "is_active": users_table.c.is_active,
        },
        column_prefix="_",
    )
