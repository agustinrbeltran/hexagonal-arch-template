from domain.shared.errors import DomainError


class SessionNotFoundError(DomainError):
    pass


class SessionExpiredError(DomainError):
    pass
