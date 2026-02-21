from core.domain.profile.events import ProfileCreated, ProfileUpdated, UsernameChanged
from core.domain.profile.value_objects import (
    BirthDate,
    FirstName,
    LastName,
    ProfileId,
    Username,
)
from shared.domain.account_id import AccountId
from shared.domain.aggregate_root import AggregateRoot


class Profile(AggregateRoot[ProfileId]):
    def __init__(
        self,
        *,
        id_: ProfileId,
        account_id: AccountId,
        username: Username | None,
        first_name: FirstName | None = None,
        last_name: LastName | None = None,
        birth_date: BirthDate | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.account_id = account_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date

    @classmethod
    def create(
        cls,
        *,
        id_: ProfileId,
        account_id: AccountId,
        username: Username | None = None,
        first_name: FirstName | None = None,
        last_name: LastName | None = None,
        birth_date: BirthDate | None = None,
    ) -> "Profile":
        profile = cls(
            id_=id_,
            account_id=account_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
        )
        profile._register_event(
            ProfileCreated(
                profile_id=id_.value,
                account_id=account_id.value,
                username=username.value if username else None,
            )
        )
        return profile

    def set_username(self, username: Username) -> bool:
        if self.username == username:
            return False
        old_username = self.username.value if self.username else None
        self.username = username
        self._register_event(
            UsernameChanged(
                profile_id=self.id_.value,
                old_username=old_username,
                new_username=username.value,
            )
        )
        return True

    def update(
        self,
        *,
        first_name: FirstName | None,
        last_name: LastName | None,
        birth_date: BirthDate | None,
        username: Username | None,
    ) -> bool:
        if (
            self.first_name == first_name
            and self.last_name == last_name
            and self.birth_date == birth_date
            and self.username == username
        ):
            return False

        old_first_name = self.first_name.value if self.first_name else None
        old_last_name = self.last_name.value if self.last_name else None
        old_birth_date = self.birth_date.value if self.birth_date else None
        old_username = self.username.value if self.username else None

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.username = username

        self._register_event(
            ProfileUpdated(
                profile_id=self.id_.value,
                old_first_name=old_first_name,
                new_first_name=first_name.value if first_name else None,
                old_last_name=old_last_name,
                new_last_name=last_name.value if last_name else None,
                old_birth_date=old_birth_date,
                new_birth_date=birth_date.value if birth_date else None,
                old_username=old_username,
                new_username=username.value if username else None,
            )
        )
        return True
