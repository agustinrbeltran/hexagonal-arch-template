import logging
from uuid import UUID

from gotrue.errors import AuthApiError

from account.application.log_in.handler import AuthenticationError
from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.password_resetter import PasswordResetter
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.application.shared.token_pair_refresher import TokenPairRefresher
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.ports import AccessRevoker
from account.domain.account.value_objects import Email, RawPassword
from account.infrastructure.security.errors import (
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from shared.domain.account_id import AccountId
from supabase import Client as SupabaseClient

log = logging.getLogger(__name__)


class SupabaseAccountProvisioner(AccountProvisioner):
    def __init__(self, client: SupabaseClient) -> None:
        self._client = client

    async def register(self, email: Email, password: RawPassword) -> AccountId:
        """:raises EmailAlreadyExistsError:"""
        try:
            response = self._client.auth.admin.create_user({
                "email": email.value,
                "password": password.value.decode(),
                "email_confirm": True,
            })
        except AuthApiError as err:
            if "already been registered" in str(err).lower():
                raise EmailAlreadyExistsError(email.value) from err
            raise

        user_id = UUID(response.user.id)
        log.info(
            "Supabase user created. ID: '%s', email: '%s'.",
            user_id,
            email.value,
        )
        return AccountId(user_id)


class SupabaseTokenPairIssuer(TokenPairIssuer):
    def __init__(
        self,
        client: SupabaseClient,
        access_token_expiry_s: int,
    ) -> None:
        self._client = client
        self._access_token_expiry_s = access_token_expiry_s

    @property
    def access_token_expiry_seconds(self) -> int:
        return self._access_token_expiry_s

    async def issue_token_pair(
        self, email: Email, password: RawPassword
    ) -> tuple[str, str]:
        """:raises AuthenticationError:"""
        try:
            response = self._client.auth.sign_in_with_password({
                "email": email.value,
                "password": password.value.decode(),
            })
        except AuthApiError as err:
            raise AuthenticationError(str(err)) from err

        session = response.session
        if session is None:
            raise AuthenticationError("No session returned from auth provider.")

        return session.access_token, session.refresh_token


class SupabaseTokenPairRefresher(TokenPairRefresher):
    def __init__(
        self,
        client: SupabaseClient,
        access_token_expiry_s: int,
    ) -> None:
        self._client = client
        self._access_token_expiry_s = access_token_expiry_s

    @property
    def access_token_expiry_seconds(self) -> int:
        return self._access_token_expiry_s

    async def refresh(self, refresh_token_id: str) -> tuple[str, str]:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        try:
            response = self._client.auth.refresh_session(refresh_token_id)
        except AuthApiError as err:
            err_msg = str(err).lower()
            if "expired" in err_msg:
                raise RefreshTokenExpiredError("Refresh token expired.") from err
            raise RefreshTokenNotFoundError(
                "Refresh token not found or invalid."
            ) from err

        session = response.session
        if session is None:
            raise RefreshTokenNotFoundError("No session returned from auth provider.")

        return session.access_token, session.refresh_token


class SupabaseAccessRevoker(AccessRevoker):
    def __init__(self, client: SupabaseClient) -> None:
        self._client = client

    async def remove_all_account_access(self, account_id: AccountId) -> None:
        try:
            self._client.auth.admin.sign_out(str(account_id.value), scope="global")
        except AuthApiError:
            log.warning(
                "Failed to revoke sessions for account '%s'. "
                "Sessions may have already expired.",
                account_id.value,
            )


class SupabasePasswordResetter(PasswordResetter):
    def __init__(self, client: SupabaseClient) -> None:
        self._client = client

    async def reset_password(
        self, account_id: AccountId, new_password: RawPassword
    ) -> None:
        self._client.auth.admin.update_user_by_id(
            str(account_id.value),
            {"password": new_password.value.decode()},
        )
        log.info(
            "Password reset for account '%s' via Supabase admin API.",
            account_id.value,
        )
