from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from domain.refresh_token.entity import RefreshToken
from domain.refresh_token.repository import RefreshTokenRepository
from domain.user.value_objects import UserId
from infrastructure.persistence.constants import DB_QUERY_FAILED
from infrastructure.persistence.errors import DataMapperError
from infrastructure.persistence.types_ import AuthAsyncSession


class SqlaRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    def add(self, token: RefreshToken) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(token)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_by_id(self, token_id: str) -> RefreshToken | None:
        """:raises DataMapperError:"""
        try:
            return await self._session.get(RefreshToken, token_id)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def delete(self, token_id: str) -> None:
        """:raises DataMapperError:"""
        stmt = delete(RefreshToken).where(RefreshToken.id_ == token_id)  # type: ignore
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def delete_all_for_user(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)  # type: ignore
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
