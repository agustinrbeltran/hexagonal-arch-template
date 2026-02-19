from core.domain.profile.entity import Profile
from core.domain.profile.value_objects import ProfileId, Username
from shared.domain.account_id import AccountId
from tests.app.unit.factories.value_objects import create_account_id, create_profile_id


def create_profile(
    profile_id: ProfileId | None = None,
    account_id: AccountId | None = None,
    username: Username | None = None,
) -> Profile:
    return Profile(
        id_=profile_id or create_profile_id(),
        account_id=account_id or create_account_id(),
        username=username,
    )
