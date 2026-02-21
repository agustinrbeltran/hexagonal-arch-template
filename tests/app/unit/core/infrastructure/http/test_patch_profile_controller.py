"""
Unit tests for the PATCH /profiles/me controller logic.
Verifies that PatchProfileCommand is built correctly using model_fields_set.
"""

from datetime import date

from core.application.patch_profile.command import PatchProfileCommand
from core.infrastructure.http.controllers.update_profile import UpdateProfileBody
from shared.domain.unset import UNSET, Unset


def _build_patch_command(body: UpdateProfileBody) -> PatchProfileCommand:
    """Replicate the controller's command-building logic."""
    fields = body.model_fields_set
    return PatchProfileCommand(
        first_name=body.first_name if "first_name" in fields else UNSET,
        last_name=body.last_name if "last_name" in fields else UNSET,
        birth_date=body.birth_date if "birth_date" in fields else UNSET,
        username=body.username if "username" in fields else UNSET,
    )


def test_partial_body_only_provided_fields_in_command() -> None:
    body = UpdateProfileBody.model_validate({"first_name": "Andres"})

    command = _build_patch_command(body)

    assert command.first_name == "Andres"
    assert isinstance(command.last_name, Unset)
    assert isinstance(command.birth_date, Unset)
    assert isinstance(command.username, Unset)


def test_explicit_null_field_is_none_not_unset() -> None:
    body = UpdateProfileBody.model_validate({"birth_date": None})

    command = _build_patch_command(body)

    assert command.birth_date is None
    assert isinstance(command.first_name, Unset)
    assert isinstance(command.last_name, Unset)
    assert isinstance(command.username, Unset)


def test_empty_body_all_fields_are_unset() -> None:
    body = UpdateProfileBody.model_validate({})

    command = _build_patch_command(body)

    assert isinstance(command.first_name, Unset)
    assert isinstance(command.last_name, Unset)
    assert isinstance(command.birth_date, Unset)
    assert isinstance(command.username, Unset)


def test_full_body_all_fields_set() -> None:
    body = UpdateProfileBody.model_validate({
        "first_name": "Andres",
        "last_name": "Garcia",
        "birth_date": "2000-01-01",
        "username": "andres_g99",
    })

    command = _build_patch_command(body)

    assert command.first_name == "Andres"
    assert command.last_name == "Garcia"
    assert command.birth_date == date(2000, 1, 1)
    assert command.username == "andres_g99"
