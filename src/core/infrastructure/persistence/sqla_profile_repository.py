from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from core.domain.profile.entity import Profile
from core.domain.profile.repository import (
    ListProfilesQM,
    ProfileQueryModel,
    ProfileRepository,
)
from core.domain.profile.value_objects import ProfileId
from core.infrastructure.persistence.converters.profile_converter import (
    ProfileConverter,
)
from core.infrastructure.persistence.mappers.profile import (
    ProfileRecord,
    profiles_table,
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


class SqlaProfileRepository(ProfileRepository):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    def save(self, profile: Profile) -> None:
        """:raises DataMapperError:"""
        try:
            record = ProfileConverter.to_record(profile)
            self._session.sync_session.merge(record)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def get_by_id(
        self,
        profile_id: ProfileId,
        for_update: bool = False,
    ) -> Profile | None:
        """:raises DataMapperError:"""
        stmt = select(ProfileRecord).where(
            ProfileRecord.id == profile_id.value  # type: ignore[arg-type]
        )

        if for_update:
            stmt = stmt.with_for_update()

        try:
            record = (await self._session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        return ProfileConverter.to_entity(record) if record else None

    async def get_by_account_id(
        self,
        account_id: AccountId,
        for_update: bool = False,
    ) -> Profile | None:
        """:raises DataMapperError:"""
        stmt = select(ProfileRecord).where(
            ProfileRecord.account_id == account_id.value  # type: ignore[arg-type]
        )

        if for_update:
            stmt = stmt.with_for_update()

        try:
            record = (await self._session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        return ProfileConverter.to_entity(record) if record else None

    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListProfilesQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
        sorting_col = profiles_table.c.get(sorting.field)
        if sorting_col is None:
            raise SortingError(f"Invalid sorting field: '{sorting.field}'")

        order_by = (
            sorting_col.asc()
            if sorting.order == SortingOrder.ASC
            else sorting_col.desc()
        )

        stmt = (
            select(
                profiles_table.c.id,
                profiles_table.c.account_id,
                profiles_table.c.username,
                func.count().over().label("total"),
            )
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
            return ListProfilesQM(profiles=[], total=0)

        profiles = [
            ProfileQueryModel(
                id_=row.id,
                account_id=row.account_id,
                username=row.username,
            )
            for row in rows
        ]
        total = rows[0].total
        return ListProfilesQM(profiles=profiles, total=total)
