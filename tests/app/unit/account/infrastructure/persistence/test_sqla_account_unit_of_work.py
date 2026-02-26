from typing import NamedTuple, cast
from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from account.domain.account.errors import EmailAlreadyExistsError
from account.infrastructure.persistence.sqla_account_unit_of_work import (
    SqlaAccountUnitOfWork,
)
from shared.infrastructure.persistence.errors import DataMapperError
from shared.infrastructure.persistence.types_ import MainAsyncSession


class _FakeDiag(NamedTuple):
    constraint_name: str | None


class _FakePgError(Exception):
    def __init__(
        self,
        *,
        constraint_name: str | None,
        sqlstate: str = "23505",
    ) -> None:
        super().__init__(
            "duplicate key value violates unique constraint "
            "DETAIL:  Key (email)=(existing@example.com) already exists."
        )
        self.diag = _FakeDiag(constraint_name)
        self.sqlstate = sqlstate


def _make_session() -> AsyncMock:
    return cast(AsyncMock, create_autospec(AsyncSession, instance=True))


def _make_integrity_error(
    *,
    constraint_name: str | None,
    sqlstate: str = "23505",
) -> IntegrityError:
    return IntegrityError(
        "INSERT INTO accounts (...) VALUES (...)",
        {"email": "existing@example.com"},
        _FakePgError(constraint_name=constraint_name, sqlstate=sqlstate),
    )


class TestSqlaAccountUnitOfWorkCommit:
    @pytest.mark.asyncio
    async def test_commit_flushes_and_commits(self) -> None:
        session = _make_session()
        sut = SqlaAccountUnitOfWork(session=cast(MainAsyncSession, session))

        await sut.commit()

        session.flush.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_maps_legacy_users_username_constraint_to_email_exists_error(
        self,
    ) -> None:
        session = _make_session()
        session.flush.side_effect = _make_integrity_error(
            constraint_name="users_username_key"
        )
        sut = SqlaAccountUnitOfWork(session=cast(MainAsyncSession, session))

        with pytest.raises(EmailAlreadyExistsError, match=r"existing@example\.com"):
            await sut.commit()

        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_maps_other_integrity_errors_to_data_mapper_error(self) -> None:
        session = _make_session()
        session.flush.side_effect = _make_integrity_error(
            constraint_name="accounts_role_key"
        )
        sut = SqlaAccountUnitOfWork(session=cast(MainAsyncSession, session))

        with pytest.raises(DataMapperError, match=r"Database constraint violation\."):
            await sut.commit()

        session.commit.assert_not_awaited()
