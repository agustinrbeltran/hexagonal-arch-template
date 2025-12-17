from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from common.adapter.constants import DB_QUERY_FAILED
from common.adapter.exceptions.gateway import DataMapperError
from features.account.adapter.types_ import AuthAsyncSession
from features.account.domain.core.entities.auth_session import AuthSession
from features.account.domain.port.outbound.auth_session_gateway import (
    AuthSessionGateway,
)
from features.user.domain.core.vo.user_id import UserId


class SqlaAuthSessionGatewayAdapter(AuthSessionGateway):
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    def add(self, auth_session: AuthSession) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(auth_session)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def read_by_id(
        self,
        auth_session_id: str,
        for_update: bool = False,
    ) -> AuthSession | None:
        """:raises DataMapperError:"""
        try:
            return await self._session.get(
                AuthSession,
                auth_session_id,
                with_for_update=for_update,
            )
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def update(self, auth_session: AuthSession) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.merge(auth_session)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def delete(self, auth_session_id: str) -> None:
        """:raises DataMapperError:"""
        stmt = delete(AuthSession).where(AuthSession.id_ == auth_session_id)  # type: ignore
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def delete_all_for_user(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        stmt = delete(AuthSession).where(AuthSession.user_id == user_id)  # type: ignore
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
