import datetime as _dt
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import ClassVar, Final
from uuid import UUID

from shared.domain.errors import DomainTypeError
from shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class ProfileId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 5
    MAX_LEN: ClassVar[Final[int]] = 20

    PATTERN_START: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]",
    )
    PATTERN_ALLOWED_CHARS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"[a-zA-Z0-9._-]*",
    )
    PATTERN_NO_CONSECUTIVE_SPECIALS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]+([._-]?[a-zA-Z0-9]+)*[._-]?$",
    )
    PATTERN_END: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r".*[a-zA-Z0-9]$",
    )

    value: str

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        self._validate_username_length(self.value)
        self._validate_username_pattern(self.value)

    def _validate_username_length(self, username_value: str) -> None:
        """:raises DomainTypeError:"""
        if len(username_value) < self.MIN_LEN or len(username_value) > self.MAX_LEN:
            raise DomainTypeError(
                f"Username must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )

    def _validate_username_pattern(self, username_value: str) -> None:
        """:raises DomainTypeError:"""
        if not re.match(self.PATTERN_START, username_value):
            raise DomainTypeError(
                "Username must start with a letter (A-Z, a-z) or a digit (0-9).",
            )
        if not re.fullmatch(self.PATTERN_ALLOWED_CHARS, username_value):
            raise DomainTypeError(
                "Username can only contain letters (A-Z, a-z), digits (0-9), "
                "dots (.), hyphens (-), and underscores (_).",
            )
        if not re.fullmatch(self.PATTERN_NO_CONSECUTIVE_SPECIALS, username_value):
            raise DomainTypeError(
                "Username cannot contain consecutive special characters"
                " like .., --, or __.",
            )
        if not re.match(self.PATTERN_END, username_value):
            raise DomainTypeError(
                "Username must end with a letter (A-Z, a-z) or a digit (0-9).",
            )


@dataclass(frozen=True, slots=True, repr=False)
class FirstName(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 50

    value: str

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        trimmed = self.value.strip()
        if len(trimmed) < self.MIN_LEN or len(trimmed) > self.MAX_LEN:
            raise DomainTypeError(
                f"First name must be between {self.MIN_LEN} "
                f"and {self.MAX_LEN} characters.",
            )


@dataclass(frozen=True, slots=True, repr=False)
class LastName(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 50

    value: str

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        trimmed = self.value.strip()
        if len(trimmed) < self.MIN_LEN or len(trimmed) > self.MAX_LEN:
            raise DomainTypeError(
                f"Last name must be between {self.MIN_LEN} "
                f"and {self.MAX_LEN} characters.",
            )


@dataclass(frozen=True, slots=True, repr=False)
class BirthDate(ValueObject):
    """raises DomainTypeError"""

    MAX_AGE_YEARS: ClassVar[Final[int]] = 150

    value: date

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        today = _dt.datetime.now(tz=_dt.UTC).date()
        if self.value >= today:
            raise DomainTypeError("Birth date must be in the past.")
        min_date = today - timedelta(days=self.MAX_AGE_YEARS * 365)
        if self.value < min_date:
            raise DomainTypeError(
                f"Birth date cannot be more than {self.MAX_AGE_YEARS} years ago.",
            )
