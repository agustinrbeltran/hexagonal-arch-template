from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import Email
from account.infrastructure.persistence.sqla_account_repository import (
    SqlaAccountRepository,
)
from shared.domain.account_id import AccountId
from shared.domain.queries import (
    OffsetPaginationParams,
    SortingError,
    SortingOrder,
    SortingParams,
)
from shared.infrastructure.persistence.errors import DataMapperError, ReaderError
from tests.app.unit.factories.account_entity import create_account


def _make_row(
    *,
    id_: object | None = None,
    email: str = "user@example.com",
    role: AccountRole = AccountRole.USER,
    is_active: bool = True,
    total: int | None = None,
) -> MagicMock:
    row = MagicMock()
    row.id = id_ or uuid4()
    row.email = email
    row.role = role
    row.is_active = is_active
    if total is not None:
        row.total = total
    return row


class TestSave:
    @pytest.mark.asyncio
    async def test_merge_called_with_correct_record(self) -> None:
        session = AsyncMock()
        repo = SqlaAccountRepository(session)
        account = create_account()

        await repo.save(account)

        session.merge.assert_awaited_once()
        record = session.merge.call_args[0][0]
        assert record.account_id == account.id_.value
        assert record.role == account.role
        assert record.is_active == account.is_active

    @pytest.mark.asyncio
    async def test_sqla_error_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.merge.side_effect = SQLAlchemyError("db error")
        repo = SqlaAccountRepository(session)

        with pytest.raises(DataMapperError):
            await repo.save(create_account())


class TestGetById:
    @pytest.mark.asyncio
    async def test_found_returns_account(self) -> None:
        uid = uuid4()
        row = _make_row(id_=uid, email="found@example.com", role=AccountRole.ADMIN)
        result = MagicMock()
        result.one_or_none.return_value = row

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        account = await repo.get_by_id(AccountId(uid))

        assert account is not None
        assert account.id_.value == uid
        assert account.email.value == "found@example.com"
        assert account.role == AccountRole.ADMIN

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self) -> None:
        result = MagicMock()
        result.one_or_none.return_value = None

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        assert await repo.get_by_id(AccountId(uuid4())) is None

    @pytest.mark.asyncio
    async def test_for_update_flag_applied(self) -> None:
        result = MagicMock()
        result.one_or_none.return_value = None

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        await repo.get_by_id(AccountId(uuid4()), for_update=True)

        stmt = session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "FOR UPDATE" in compiled

    @pytest.mark.asyncio
    async def test_sqla_error_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.execute.side_effect = SQLAlchemyError("db error")
        repo = SqlaAccountRepository(session)

        with pytest.raises(DataMapperError):
            await repo.get_by_id(AccountId(uuid4()))


class TestGetByEmail:
    @pytest.mark.asyncio
    async def test_found_returns_account(self) -> None:
        uid = uuid4()
        row = _make_row(id_=uid, email="found@example.com")
        result = MagicMock()
        result.one_or_none.return_value = row

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        account = await repo.get_by_email(Email("found@example.com"))

        assert account is not None
        assert account.id_.value == uid

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self) -> None:
        result = MagicMock()
        result.one_or_none.return_value = None

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        assert await repo.get_by_email(Email("missing@example.com")) is None

    @pytest.mark.asyncio
    async def test_sqla_error_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.execute.side_effect = SQLAlchemyError("db error")
        repo = SqlaAccountRepository(session)

        with pytest.raises(DataMapperError):
            await repo.get_by_email(Email("err@example.com"))


class TestGetAll:
    @pytest.mark.asyncio
    async def test_paginated_results(self) -> None:
        uid1, uid2 = uuid4(), uuid4()
        rows = [
            _make_row(id_=uid1, email="a@example.com", total=5),
            _make_row(id_=uid2, email="b@example.com", total=5),
        ]
        result = MagicMock()
        result.all.return_value = rows

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        qm = await repo.get_all(
            pagination=OffsetPaginationParams(limit=10, offset=0),
            sorting=SortingParams(field="email", order=SortingOrder.ASC),
        )

        assert qm["total"] == 5
        assert len(qm["accounts"]) == 2
        assert qm["accounts"][0]["id_"] == uid1

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        result = MagicMock()
        result.all.return_value = []

        session = AsyncMock()
        session.execute.return_value = result
        repo = SqlaAccountRepository(session)

        qm = await repo.get_all(
            pagination=OffsetPaginationParams(limit=10, offset=0),
            sorting=SortingParams(field="email", order=SortingOrder.ASC),
        )

        assert qm["total"] == 0
        assert qm["accounts"] == []

    @pytest.mark.asyncio
    async def test_invalid_sorting_field_raises(self) -> None:
        session = AsyncMock()
        repo = SqlaAccountRepository(session)

        with pytest.raises(SortingError, match="Invalid sorting field"):
            await repo.get_all(
                pagination=OffsetPaginationParams(limit=10, offset=0),
                sorting=SortingParams(field="nonexistent", order=SortingOrder.ASC),
            )

    @pytest.mark.asyncio
    async def test_sqla_error_raises_reader_error(self) -> None:
        session = AsyncMock()
        session.execute.side_effect = SQLAlchemyError("db error")
        repo = SqlaAccountRepository(session)

        with pytest.raises(ReaderError):
            await repo.get_all(
                pagination=OffsetPaginationParams(limit=10, offset=0),
                sorting=SortingParams(field="email", order=SortingOrder.ASC),
            )
