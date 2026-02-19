from core.domain.profile.entity import Profile
from core.domain.profile.value_objects import ProfileId, Username
from core.infrastructure.persistence.mappers.profile import ProfileRecord
from shared.domain.account_id import AccountId


class ProfileConverter:
    @staticmethod
    def to_entity(record: ProfileRecord) -> Profile:
        return Profile(
            id_=ProfileId(record.id),
            account_id=AccountId(record.account_id),
            username=Username(record.username) if record.username else None,
        )

    @staticmethod
    def to_record(entity: Profile) -> ProfileRecord:
        return ProfileRecord(
            id=entity.id_.value,
            account_id=entity.account_id.value,
            username=entity.username.value if entity.username else None,
        )
