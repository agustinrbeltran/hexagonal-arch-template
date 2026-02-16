from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from domain.auth_session.entity import AuthSession
from domain.auth_session.gateway import AuthSessionGateway
from domain.user.value_objects import UserId
from infrastructure.persistence.constants import DB_QUERY_FAILED
from infrastructure.persistence.errors import DataMapperError
from infrastructure.persistence.types_ import AuthAsyncSession


class SqlaAuthSessionGateway(AuthSessionGateway):
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
