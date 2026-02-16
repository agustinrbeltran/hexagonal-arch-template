from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from domain.shared.queries import (
    OffsetPaginationParams,
    SortingError,
    SortingOrder,
    SortingParams,
)
from domain.user.entity import User
from domain.user.repository import ListUsersQM, UserQueryModel, UserRepository
from domain.user.value_objects import UserId, Username
from infrastructure.persistence.constants import DB_QUERY_FAILED
from infrastructure.persistence.errors import DataMapperError, ReaderError
from infrastructure.persistence.mappers.user import users_table
from infrastructure.persistence.types_ import MainAsyncSession


class SqlaUserRepository(UserRepository):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    def save(self, user: User) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(user)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_by_id(
        self,
        user_id: UserId,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""
        stmt = select(User).where(User.id_ == user_id)  # type: ignore

        if for_update:
            stmt = stmt.with_for_update()

        try:
            return (await self._session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""
        stmt = select(User).where(User.username == username)  # type: ignore

        if for_update:
            stmt = stmt.with_for_update()

        try:
            return (await self._session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
        sorting_col = users_table.c.get(sorting.field)
        if sorting_col is None:
            raise SortingError(f"Invalid sorting field: '{sorting.field}'")

        order_by = (
            sorting_col.asc()
            if sorting.order == SortingOrder.ASC
            else sorting_col.desc()
        )

        stmt = (
            select(
                users_table.c.id,
                users_table.c.username,
                users_table.c.role,
                users_table.c.is_active,
                func.count().over().label("total"),
            )
            .order_by(order_by)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        try:
            result = await self._session.execute(stmt)
            rows = result.all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        if not rows:
            return ListUsersQM(users=[], total=0)

        users = [
            UserQueryModel(
                id_=row.id,
                username=row.username,
                role=row.role,
                is_active=row.is_active,
            )
            for row in rows
        ]
        total = rows[0].total
        return ListUsersQM(users=users, total=total)
