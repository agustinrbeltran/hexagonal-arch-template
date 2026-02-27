from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from account.infrastructure.persistence.sqla_account_unit_of_work import (
    SqlaAccountUnitOfWork,
)
from shared.infrastructure.persistence.errors import DataMapperError


class TestCommit:
    @pytest.mark.asyncio
    async def test_flush_then_commit_order(self) -> None:
        call_order: list[str] = []

        def track_flush() -> None:
            call_order.append("flush")

        def track_commit() -> None:
            call_order.append("commit")

        session = AsyncMock()
        session.flush.side_effect = track_flush
        session.commit.side_effect = track_commit

        uow = SqlaAccountUnitOfWork(session)
        await uow.commit()

        assert call_order == ["flush", "commit"]

    @pytest.mark.asyncio
    async def test_integrity_error_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.flush.side_effect = IntegrityError(
            "duplicate", params=None, orig=Exception()
        )

        uow = SqlaAccountUnitOfWork(session)

        with pytest.raises(DataMapperError, match="constraint violation"):
            await uow.commit()

    @pytest.mark.asyncio
    async def test_sqla_error_on_flush_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.flush.side_effect = SQLAlchemyError("flush failed")

        uow = SqlaAccountUnitOfWork(session)

        with pytest.raises(DataMapperError, match="query failed"):
            await uow.commit()

    @pytest.mark.asyncio
    async def test_sqla_error_on_commit_raises_data_mapper_error(self) -> None:
        session = AsyncMock()
        session.commit.side_effect = SQLAlchemyError("commit failed")

        uow = SqlaAccountUnitOfWork(session)

        with pytest.raises(DataMapperError, match="query failed"):
            await uow.commit()


class TestRollback:
    @pytest.mark.asyncio
    async def test_rollback_delegates_to_session(self) -> None:
        session = AsyncMock()

        uow = SqlaAccountUnitOfWork(session)
        await uow.rollback()

        session.rollback.assert_awaited_once()
