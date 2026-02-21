from datetime import date

from core.domain.profile.events import ProfilePatchApplied
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, Username
from shared.domain.unset import UNSET
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import create_username


def test_apply_patch_partial_mutation_only_provided_fields() -> None:
    fn = FirstName("Alice")
    ln = LastName("Smith")
    bd = BirthDate(date(1990, 6, 15))
    uname = create_username("alice_s123")
    profile = create_profile(username=uname, first_name=fn, last_name=ln, birth_date=bd)

    result = profile.apply_patch(first_name=FirstName("Andres"))

    assert result is True
    assert profile.first_name == FirstName("Andres")
    assert profile.last_name == ln
    assert profile.birth_date == bd
    assert profile.username == uname


def test_apply_patch_registers_event_with_delta() -> None:
    fn = FirstName("Alice")
    ln = LastName("Smith")
    profile = create_profile(username=None, first_name=fn, last_name=ln)

    profile.apply_patch(first_name=FirstName("Andres"))

    events = profile.collect_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ProfilePatchApplied)
    assert event.first_name == ("Alice", "Andres")
    assert event.last_name is None
    assert event.birth_date is None
    assert event.username is None


def test_apply_patch_unset_fields_are_skipped() -> None:
    fn = FirstName("Alice")
    profile = create_profile(username=None, first_name=fn)

    result = profile.apply_patch(username=UNSET)

    assert result is False
    assert profile.first_name == fn
    events = profile.collect_events()
    assert len(events) == 0


def test_apply_patch_explicit_none_clears_field() -> None:
    bd = BirthDate(date(1990, 1, 1))
    profile = create_profile(username=None, birth_date=bd)

    result = profile.apply_patch(birth_date=None)

    assert result is True
    assert profile.birth_date is None
    events = profile.collect_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ProfilePatchApplied)
    assert event.birth_date == (date(1990, 1, 1), None)


def test_apply_patch_noop_returns_false() -> None:
    fn = FirstName("Andres")
    profile = create_profile(username=None, first_name=fn)

    result = profile.apply_patch(first_name=FirstName("Andres"))

    assert result is False
    events = profile.collect_events()
    assert len(events) == 0


def test_apply_patch_all_fields_changed() -> None:
    old_fn = FirstName("Alice")
    old_ln = LastName("Smith")
    old_bd = BirthDate(date(1990, 6, 15))
    old_uname = Username("alice_s123")
    profile = create_profile(
        username=old_uname,
        first_name=old_fn,
        last_name=old_ln,
        birth_date=old_bd,
    )

    new_fn = FirstName("Andres")
    new_ln = LastName("Garcia")
    new_bd = BirthDate(date(2000, 1, 1))
    new_uname = Username("andres_g99")

    result = profile.apply_patch(
        first_name=new_fn,
        last_name=new_ln,
        birth_date=new_bd,
        username=new_uname,
    )

    assert result is True
    events = profile.collect_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ProfilePatchApplied)
    assert event.first_name == ("Alice", "Andres")
    assert event.last_name == ("Smith", "Garcia")
    assert event.birth_date == (date(1990, 6, 15), date(2000, 1, 1))
    assert event.username == ("alice_s123", "andres_g99")


def test_apply_patch_all_unset_no_event() -> None:
    profile = create_profile(username=None)

    result = profile.apply_patch()

    assert result is False
    events = profile.collect_events()
    assert len(events) == 0
