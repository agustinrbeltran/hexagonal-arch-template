from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from common.adapter.constants import DB_QUERY_FAILED
from common.adapter.exceptions.gateway import DataMapperError, ReaderError
from common.adapter.types_ import MainAsyncSession
from common.domain.core.exceptions.query import SortingError
from common.domain.port.inbound.queries.offset_pagination import OffsetPaginationParams
from common.domain.port.inbound.queries.sorting import SortingOrder, SortingParams
from features.user.adapter.mapper.user import users_table
from features.user.domain.core.entities.user import User
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.core.vo.username import Username
from features.user.domain.port.outbound.queries.user_queries import (
    ListUsersQM,
    UserQueryModel,
)
from features.user.domain.port.outbound.user_repository import UserRepository


class SqlaUserRepositoryAdapter(UserRepository):
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
