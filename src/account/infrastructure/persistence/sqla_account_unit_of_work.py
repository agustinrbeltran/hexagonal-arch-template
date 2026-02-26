import logging
from collections.abc import Mapping
from typing import Any, Final, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.errors import EmailAlreadyExistsError
from shared.infrastructure.persistence.constants import (
    DB_COMMIT_DONE,
    DB_COMMIT_FAILED,
    DB_CONSTRAINT_VIOLATION,
    DB_QUERY_FAILED,
)
from shared.infrastructure.persistence.errors import DataMapperError
from shared.infrastructure.persistence.types_ import MainAsyncSession

log = logging.getLogger(__name__)

UNIQUE_VIOLATION_SQLSTATE: Final[str] = "23505"
EMAIL_UNIQUE_CONSTRAINT_NAMES: Final[frozenset[str]] = frozenset(
    {"uq_accounts_email", "accounts_email_key", "users_username_key"}
)


def _is_email_unique_violation(err: IntegrityError) -> bool:
    diag = getattr(err.orig, "diag", None)
    constraint_name = getattr(diag, "constraint_name", None)
    if constraint_name in EMAIL_UNIQUE_CONSTRAINT_NAMES:
        return True

    sqlstate = getattr(err.orig, "sqlstate", None) or getattr(err.orig, "pgcode", None)
    if sqlstate != UNIQUE_VIOLATION_SQLSTATE:
        return False

    error_text = str(err).lower()
    return "(email)=" in error_text


def _extract_email(params: Any) -> str:
    if isinstance(params, Mapping):
        email = params.get("email")
        if email is not None:
            return str(email)
    return "unknown"


class SqlaAccountUnitOfWork(AccountUnitOfWork):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """
        :raises DataMapperError:
        :raises EmailAlreadyExistsError:
        """
        try:
            await self._session.flush()
        except IntegrityError as err:
            log.error("IntegrityError during flush: %s", err)
            if _is_email_unique_violation(err):
                params: Mapping[str, Any] = cast(Mapping[str, Any], err.params)
                email = _extract_email(params)
                raise EmailAlreadyExistsError(email) from err
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
