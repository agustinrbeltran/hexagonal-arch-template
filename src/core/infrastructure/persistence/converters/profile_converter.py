from core.domain.profile.entity import Profile
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, ProfileId, Username
from core.infrastructure.persistence.mappers.profile import ProfileRecord
from shared.domain.account_id import AccountId


class ProfileConverter:
    @staticmethod
    def to_entity(record: ProfileRecord) -> Profile:
        return Profile(
            id_=ProfileId(record.id),
            account_id=AccountId(record.account_id),
            username=Username(record.username) if record.username else None,
            first_name=FirstName(record.first_name) if record.first_name else None,
            last_name=LastName(record.last_name) if record.last_name else None,
            birth_date=BirthDate(record.birth_date) if record.birth_date else None,
        )

    @staticmethod
    def to_record(entity: Profile) -> ProfileRecord:
        return ProfileRecord(
            id=entity.id_.value,
            account_id=entity.account_id.value,
            username=entity.username.value if entity.username else None,
            first_name=entity.first_name.value if entity.first_name else None,
            last_name=entity.last_name.value if entity.last_name else None,
            birth_date=entity.birth_date.value if entity.birth_date else None,
        )
