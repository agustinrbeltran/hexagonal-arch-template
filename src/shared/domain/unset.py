from typing import Final


class _Unset:
    """Sentinel type to distinguish "field not provided" from None (explicit clear)."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "UNSET"


UNSET: Final[_Unset] = _Unset()
