class SecurityError(Exception):
    pass


class RefreshTokenNotFoundError(SecurityError):
    pass


class RefreshTokenExpiredError(SecurityError):
    pass
