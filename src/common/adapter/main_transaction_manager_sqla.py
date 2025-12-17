import logging

from sqlalchemy.exc import SQLAlchemyError

from common.adapter.constants import DB_COMMIT_DONE, DB_COMMIT_FAILED, \
    DB_QUERY_FAILED
from common.adapter.exceptions.gateway import DataMapperError
from common.adapter.types_ import MainAsyncSession
from common.domain.port.outbound.transaction_manager import (
    TransactionManager,
)


log = logging.getLogger(__name__)


class SqlaMainTransactionManager(TransactionManager):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.commit()
            log.debug("%s Main session.", DB_COMMIT_DONE)

        except SQLAlchemyError as err:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from err
