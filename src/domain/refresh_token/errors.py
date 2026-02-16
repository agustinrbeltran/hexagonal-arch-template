from domain.shared.errors import DomainError


class RefreshTokenNotFoundError(DomainError):
    pass


class RefreshTokenExpiredError(DomainError):
    pass
