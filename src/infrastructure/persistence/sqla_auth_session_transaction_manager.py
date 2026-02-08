import logging

from sqlalchemy.exc import SQLAlchemyError

from domain.auth_session.ports import AuthSessionTransactionManager
from infrastructure.persistence.constants import (
    DB_COMMIT_DONE,
    DB_COMMIT_FAILED,
    DB_QUERY_FAILED,
)
from infrastructure.persistence.errors import DataMapperError
from infrastructure.persistence.types_ import AuthAsyncSession

log = logging.getLogger(__name__)


class SqlaAuthSessionTransactionManager(AuthSessionTransactionManager):
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.commit()
            log.debug("%s Auth session.", DB_COMMIT_DONE)

        except SQLAlchemyError as err:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from err
