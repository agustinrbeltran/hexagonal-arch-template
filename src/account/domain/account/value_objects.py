import re
from dataclasses import dataclass, field
from typing import ClassVar, Final

from shared.domain.errors import DomainTypeError
from shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Email(ValueObject):
    """raises DomainTypeError"""

    MAX_LEN: ClassVar[Final[int]] = 255
    PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    value: str

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        if len(self.value) > self.MAX_LEN:
            raise DomainTypeError(
                f"Email must be at most {self.MAX_LEN} characters long."
            )
        if not re.fullmatch(self.PATTERN, self.value):
            raise DomainTypeError("Invalid email format.")


@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 6

    value: bytes = field(init=False, repr=False)

    def __init__(self, value: str) -> None:
        """:raises DomainTypeError:"""
        self._validate_password_length(value)
        object.__setattr__(self, "value", value.encode())

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainTypeError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainTypeError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )
