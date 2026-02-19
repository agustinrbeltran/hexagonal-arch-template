from core.domain.profile.entity import Profile
from core.domain.profile.events import ProfileCreated, UsernameChanged
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


def test_set_username_changes_and_registers_event() -> None:
    old_username = create_username("olduser1")
    new_username = create_username("newuser1")
    profile = create_profile(username=old_username)

    result = profile.set_username(new_username)

    assert result is True
    assert profile.username == new_username
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], UsernameChanged)
    assert events[0].old_username == old_username.value
    assert events[0].new_username == new_username.value


def test_set_username_same_returns_false_no_event() -> None:
    username = create_username("sameuser")
    profile = create_profile(username=username)

    result = profile.set_username(username)

    assert result is False
    events = profile.collect_events()
    assert len(events) == 0


def test_set_username_from_none() -> None:
    profile = create_profile(username=None)
    new_username = create_username("first1")

    result = profile.set_username(new_username)

    assert result is True
    assert profile.username == new_username
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], UsernameChanged)
    assert events[0].old_username is None
    assert events[0].new_username == new_username.value
