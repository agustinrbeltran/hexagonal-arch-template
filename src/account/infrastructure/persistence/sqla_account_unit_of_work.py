import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from account.application.shared.account_unit_of_work import AccountUnitOfWork
from shared.infrastructure.persistence.constants import (
    DB_COMMIT_DONE,
    DB_COMMIT_FAILED,
    DB_CONSTRAINT_VIOLATION,
    DB_QUERY_FAILED,
)
from shared.infrastructure.persistence.errors import DataMapperError
from shared.infrastructure.persistence.types_ import MainAsyncSession

log = logging.getLogger(__name__)


class SqlaAccountUnitOfWork(AccountUnitOfWork):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.flush()
        except IntegrityError as err:
            log.error("IntegrityError during flush: %s", err)
            raise DataMapperError(DB_CONSTRAINT_VIOLATION) from err
        except SQLAlchemyError as err:
            log.error("SQLAlchemyError during flush: %s", err)
            raise DataMapperError(f"{DB_QUERY_FAILED}") from err

        try:
            await self._session.commit()
            log.debug("%s Main session.", DB_COMMIT_DONE)
        except SQLAlchemyError as err:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from err

    async def rollback(self) -> None:
        await self._session.rollback()
