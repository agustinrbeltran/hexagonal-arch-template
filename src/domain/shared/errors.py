class DomainError(Exception):
    """Domain rule violation not tied to domain type construction."""


class DomainTypeError(Exception):
    """Invalid construction of domain types (Value Objects)."""


class NotFoundError(DomainError):
    """Requested entity was not found."""


class AuthorizationError(DomainError):
    """Caller is not authorized to perform the action."""
