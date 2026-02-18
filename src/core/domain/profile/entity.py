from shared.domain.account_id import AccountId
from shared.domain.aggregate_root import AggregateRoot

from core.domain.profile.events import ProfileCreated, UsernameChanged
from core.domain.profile.value_objects import ProfileId, Username


class Profile(AggregateRoot[ProfileId]):
    def __init__(
        self,
        *,
        id_: ProfileId,
        account_id: AccountId,
        username: Username | None,
    ) -> None:
        super().__init__(id_=id_)
        self.account_id = account_id
        self.username = username

    @classmethod
    def create(
        cls,
        *,
        id_: ProfileId,
        account_id: AccountId,
        username: Username | None = None,
    ) -> "Profile":
        profile = cls(id_=id_, account_id=account_id, username=username)
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
