from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from account.infrastructure.security.refresh_token import RefreshToken
from account.infrastructure.security.refresh_token_repository import (
    RefreshTokenRepository,
)
from shared.domain.account_id import AccountId
from shared.infrastructure.persistence.constants import DB_QUERY_FAILED
from shared.infrastructure.persistence.errors import DataMapperError
from shared.infrastructure.persistence.types_ import AuthAsyncSession


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

    async def delete_all_for_account(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""
        stmt = delete(RefreshToken).where(RefreshToken.account_id == account_id)  # type: ignore
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
