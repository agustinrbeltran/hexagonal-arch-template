from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from account.domain.account.entity import Account
from account.domain.account.repository import (
    AccountQueryModel,
    AccountRepository,
    ListAccountsQM,
)
from account.domain.account.value_objects import Email
from account.infrastructure.persistence.converters.account_converter import (
    AccountConverter,
)
from account.infrastructure.persistence.mappers.account import (
    account_metadata_table,
    auth_users_table,
)
from shared.domain.account_id import AccountId
from shared.domain.queries import (
    OffsetPaginationParams,
    SortingError,
    SortingOrder,
    SortingParams,
)
from shared.infrastructure.persistence.constants import DB_QUERY_FAILED
from shared.infrastructure.persistence.errors import DataMapperError, ReaderError
from shared.infrastructure.persistence.types_ import MainAsyncSession

# Base join for cross-schema queries
_account_join = auth_users_table.join(
    account_metadata_table,
    auth_users_table.c.id == account_metadata_table.c.account_id,
)

# Sortable columns mapping
_SORTABLE_COLUMNS = {
    "email": auth_users_table.c.email,
    "role": account_metadata_table.c.role,
    "is_active": account_metadata_table.c.is_active,
}


class SqlaAccountRepository(AccountRepository):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def save(self, account: Account) -> None:
        """:raises DataMapperError:"""
        try:
            record = AccountConverter.to_record(account)
            await self._session.merge(record)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_by_id(
        self,
        account_id: AccountId,
        for_update: bool = False,
    ) -> Account | None:
        """:raises DataMapperError:"""
        stmt = (
            select(
                auth_users_table.c.id,
                auth_users_table.c.email,
                account_metadata_table.c.role,
                account_metadata_table.c.is_active,
            )
            .select_from(_account_join)
            .where(auth_users_table.c.id == account_id.value)
        )

        if for_update:
            stmt = stmt.with_for_update()

        try:
            row = (await self._session.execute(stmt)).one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        if row is None:
            return None

        return AccountConverter.to_entity(
            account_id=row.id,
            email=row.email,
            role=row.role,
            is_active=row.is_active,
        )

    async def get_by_email(
        self,
        email: Email,
        for_update: bool = False,
    ) -> Account | None:
        """:raises DataMapperError:"""
        stmt = (
            select(
                auth_users_table.c.id,
                auth_users_table.c.email,
                account_metadata_table.c.role,
                account_metadata_table.c.is_active,
            )
            .select_from(_account_join)
            .where(auth_users_table.c.email == email.value)
        )

        if for_update:
            stmt = stmt.with_for_update()

        try:
            row = (await self._session.execute(stmt)).one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        if row is None:
            return None

        return AccountConverter.to_entity(
            account_id=row.id,
            email=row.email,
            role=row.role,
            is_active=row.is_active,
        )

    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListAccountsQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
        sorting_col = _SORTABLE_COLUMNS.get(sorting.field)
        if sorting_col is None:
            raise SortingError(f"Invalid sorting field: '{sorting.field}'")

        order_by = (
            sorting_col.asc()
            if sorting.order == SortingOrder.ASC
            else sorting_col.desc()
        )

        stmt = (
            select(
                auth_users_table.c.id,
                auth_users_table.c.email,
                account_metadata_table.c.role,
                account_metadata_table.c.is_active,
                func.count().over().label("total"),
            )
            .select_from(_account_join)
            .order_by(order_by)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        try:
            result = await self._session.execute(stmt)
            rows = result.all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        if not rows:
            return ListAccountsQM(accounts=[], total=0)

        accounts = [
            AccountQueryModel(
                id_=row.id,
                email=row.email,
                role=row.role,
                is_active=row.is_active,
            )
            for row in rows
        ]
        total = rows[0].total
        return ListAccountsQM(accounts=accounts, total=total)
