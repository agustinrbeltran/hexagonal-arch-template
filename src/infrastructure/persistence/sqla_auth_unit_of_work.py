from sqlalchemy.exc import SQLAlchemyError

from application.shared.auth_unit_of_work import AuthUnitOfWork
from infrastructure.persistence.constants import DB_COMMIT_FAILED, DB_QUERY_FAILED
from infrastructure.persistence.errors import DataMapperError
from infrastructure.persistence.types_ import AuthAsyncSession


class SqlaAuthUnitOfWork(AuthUnitOfWork):
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.flush()
            await self._session.commit()
        except SQLAlchemyError as err:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from err

    async def rollback(self) -> None:
        await self._session.rollback()
