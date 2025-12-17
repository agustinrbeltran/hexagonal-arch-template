import logging
from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from common.adapter.constants import (
    DB_CONSTRAINT_VIOLATION,
    DB_FLUSH_DONE,
    DB_FLUSH_FAILED,
    DB_QUERY_FAILED,
)
from common.adapter.exceptions.gateway import DataMapperError
from common.adapter.types_ import MainAsyncSession
from common.domain.port.outbound.flusher import Flusher
from features.user.domain.core.exceptions.user import UsernameAlreadyExistsError

log = logging.getLogger(__name__)


class SqlaMainFlusher(Flusher):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
        try:
            await self._session.flush()
            log.debug("%s Main session.", DB_FLUSH_DONE)

        except IntegrityError as err:
            if "uq_users_username" in str(err):
                params: Mapping[str, Any] = cast(Mapping[str, Any], err.params)
                username = str(params.get("username", "unknown"))
                raise UsernameAlreadyExistsError(username) from err

            raise DataMapperError(DB_CONSTRAINT_VIOLATION) from err

        except SQLAlchemyError as err:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_FLUSH_FAILED}") from err
