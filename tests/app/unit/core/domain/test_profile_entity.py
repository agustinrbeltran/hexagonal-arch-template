from datetime import date

from core.domain.profile.entity import Profile
from core.domain.profile.events import ProfileCreated, ProfileUpdated
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, Username
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import (
    create_account_id,
    create_profile_id,
    create_username,
)


def test_create_registers_profile_created_event() -> None:
    profile_id = create_profile_id()
    account_id = create_account_id()

    profile = Profile.create(id_=profile_id, account_id=account_id)

    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], ProfileCreated)
    assert events[0].profile_id == profile_id.value
    assert events[0].account_id == account_id.value
    assert events[0].username is None


# task 2.5: Profile.create new optional fields default to None
def test_create_new_optional_fields_default_to_none() -> None:
    profile_id = create_profile_id()
    account_id = create_account_id()

    profile = Profile.create(id_=profile_id, account_id=account_id)

    assert profile.first_name is None
    assert profile.last_name is None
    assert profile.birth_date is None


def test_create_with_username_new_fields_default_to_none() -> None:
    username = create_username("johndoe1")
    profile = Profile.create(
        id_=create_profile_id(),
        account_id=create_account_id(),
        username=username,
    )
    assert profile.first_name is None
    assert profile.last_name is None
    assert profile.birth_date is None


# task 2.4: Profile.update tests
def test_update_all_fields_registers_event() -> None:
    profile = create_profile(username=None)
    fn = FirstName("Alice")
    ln = LastName("Smith")
    bd = BirthDate(date(1990, 6, 15))
    uname = Username("alice_s123")

    result = profile.update(first_name=fn, last_name=ln, birth_date=bd, username=uname)

    assert result is True
    assert profile.first_name == fn
    assert profile.last_name == ln
    assert profile.birth_date == bd
    assert profile.username == uname
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], ProfileUpdated)
    assert events[0].new_first_name == "Alice"
    assert events[0].new_last_name == "Smith"
    assert events[0].new_birth_date == date(1990, 6, 15)
    assert events[0].new_username == "alice_s123"


def test_update_clear_fields_with_none() -> None:
    fn = FirstName("Alice")
    ln = LastName("Smith")
    bd = BirthDate(date(1990, 6, 15))
    uname = Username("alice_s123")
    profile = create_profile(username=uname, first_name=fn, last_name=ln, birth_date=bd)

    result = profile.update(
        first_name=None, last_name=None, birth_date=None, username=None
    )

    assert result is True
    assert profile.first_name is None
    assert profile.last_name is None
    assert profile.birth_date is None
    assert profile.username is None
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], ProfileUpdated)
    assert events[0].old_first_name == "Alice"
    assert events[0].new_first_name is None


def test_update_idempotent_no_event() -> None:
    fn = FirstName("Alice")
    ln = LastName("Smith")
    bd = BirthDate(date(1990, 6, 15))
    uname = Username("alice_s123")
    profile = create_profile(username=uname, first_name=fn, last_name=ln, birth_date=bd)

    result = profile.update(first_name=fn, last_name=ln, birth_date=bd, username=uname)

    assert result is False
    events = profile.collect_events()
    assert len(events) == 0


def test_update_partial_sets_others_to_none() -> None:
    fn = FirstName("Bob")
    uname = Username("alice_s123")
    profile = create_profile(username=uname)

    result = profile.update(
        first_name=fn, last_name=None, birth_date=None, username=None
    )

    assert result is True
    assert profile.first_name == fn
    assert profile.last_name is None
    assert profile.birth_date is None
    assert profile.username is None
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], ProfileUpdated)
