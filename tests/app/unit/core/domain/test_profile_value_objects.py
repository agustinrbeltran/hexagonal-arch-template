import datetime as _dt
from datetime import date, timedelta

import pytest

from core.domain.profile.value_objects import BirthDate, FirstName, LastName
from shared.domain.errors import DomainTypeError


class TestFirstName:
    def test_valid_first_name(self) -> None:
        fn = FirstName("Alice")
        assert fn.value == "Alice"

    def test_empty_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            FirstName("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            FirstName("   ")

    def test_too_long_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            FirstName("A" * 51)

    def test_max_length_ok(self) -> None:
        fn = FirstName("A" * 50)
        assert fn.value == "A" * 50


class TestLastName:
    def test_valid_last_name(self) -> None:
        ln = LastName("Smith")
        assert ln.value == "Smith"

    def test_empty_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            LastName("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            LastName("   ")

    def test_too_long_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            LastName("B" * 51)

    def test_max_length_ok(self) -> None:
        ln = LastName("B" * 50)
        assert ln.value == "B" * 50


class TestBirthDate:
    def test_valid_birth_date(self) -> None:
        bd = BirthDate(date(1990, 6, 15))
        assert bd.value == date(1990, 6, 15)

    def test_future_date_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            BirthDate(date(2099, 1, 1))

    def test_today_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            BirthDate(_dt.datetime.now(tz=_dt.UTC).date())

    def test_too_far_in_past_raises(self) -> None:
        with pytest.raises(DomainTypeError):
            BirthDate(date(1800, 1, 1))

    def test_yesterday_is_valid(self) -> None:
        yesterday = _dt.datetime.now(tz=_dt.UTC).date() - timedelta(days=1)
        bd = BirthDate(yesterday)
        assert bd.value == yesterday
