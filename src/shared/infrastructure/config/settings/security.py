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
        "ES256",
    ] = Field(alias="JWT_ALGORITHM")
    access_token_expiry_min: int = Field(alias="ACCESS_TOKEN_EXPIRY_MIN", ge=1)


class SupabaseSettings(BaseModel):
    url: str = Field(alias="SUPABASE_URL")
    service_role_key: str = Field(alias="SERVICE_ROLE_KEY", min_length=32)


class SecuritySettings(BaseModel):
    auth: AuthSettings
    supabase: SupabaseSettings
