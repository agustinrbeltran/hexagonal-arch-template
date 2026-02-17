from infrastructure.persistence.errors import InfrastructureError


class PasswordHasherBusyError(InfrastructureError):
    pass


class SecurityError(Exception):
    pass


class RefreshTokenNotFoundError(SecurityError):
    pass


class RefreshTokenExpiredError(SecurityError):
    pass
