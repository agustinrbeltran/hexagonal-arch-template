from typing import Literal

from pydantic import BaseModel, Field


class AuthSettings(BaseModel):
    jwt_secret: str = Field(alias="JWT_SECRET", min_length=32)
    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ] = Field(alias="JWT_ALGORITHM")
    access_token_expiry_min: int = Field(alias="ACCESS_TOKEN_EXPIRY_MIN", ge=1)
    refresh_token_expiry_days: int = Field(alias="REFRESH_TOKEN_EXPIRY_DAYS", ge=1)


class PasswordSettings(BaseModel):
    pepper: str = Field(alias="PEPPER", min_length=32)
    hasher_work_factor: int = Field(alias="HASHER_WORK_FACTOR", ge=10)
    hasher_max_threads: int = Field(alias="HASHER_MAX_THREADS", ge=1)
    hasher_semaphore_wait_timeout_s: float = Field(
        alias="HASHER_SEMAPHORE_WAIT_TIMEOUT_S", gt=0
    )


class SecuritySettings(BaseModel):
    auth: AuthSettings
    password: PasswordSettings
