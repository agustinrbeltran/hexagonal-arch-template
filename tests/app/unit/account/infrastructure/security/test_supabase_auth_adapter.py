from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from gotrue.errors import AuthApiError

from account.application.log_in.handler import AuthenticationError
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.value_objects import Email, RawPassword
from account.infrastructure.security.errors import (
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from account.infrastructure.security.supabase_auth_adapter import (
    SupabaseAccessRevoker,
    SupabaseAccountProvisioner,
    SupabasePasswordResetter,
    SupabaseTokenPairIssuer,
    SupabaseTokenPairRefresher,
)
from shared.domain.account_id import AccountId


class TestSupabaseAccountProvisioner:
    @pytest.mark.asyncio
    async def test_register_creates_user_and_returns_account_id(self) -> None:
        client = MagicMock()
        user_id = "00000000-0000-0000-0000-000000000001"
        mock_user = Mock()
        mock_user.id = user_id
        mock_response = Mock()
        mock_response.user = mock_user
        client.auth.admin.create_user.return_value = mock_response

        sut = SupabaseAccountProvisioner(client)
        result = await sut.register(
            Email("test@example.com"), RawPassword("password123")
        )

        assert result == AccountId(UUID(user_id))
        client.auth.admin.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_raises_email_already_exists_error(self) -> None:
        client = MagicMock()
        client.auth.admin.create_user.side_effect = AuthApiError(
            "User already been registered", 422, "user_already_exists"
        )

        sut = SupabaseAccountProvisioner(client)

        with pytest.raises(EmailAlreadyExistsError):
            await sut.register(
                Email("existing@example.com"), RawPassword("password123")
            )


class TestSupabaseTokenPairIssuer:
    @pytest.mark.asyncio
    async def test_issue_token_pair_returns_tokens(self) -> None:
        client = MagicMock()
        mock_session = Mock()
        mock_session.access_token = "access-token"  # noqa: S105
        mock_session.refresh_token = "refresh-token"  # noqa: S105
        mock_response = Mock()
        mock_response.session = mock_session
        client.auth.sign_in_with_password.return_value = mock_response

        sut = SupabaseTokenPairIssuer(client, access_token_expiry_s=3600)
        access, refresh = await sut.issue_token_pair(
            Email("test@example.com"), RawPassword("password123")
        )

        assert access == "access-token"
        assert refresh == "refresh-token"
        assert sut.access_token_expiry_seconds == 3600

    @pytest.mark.asyncio
    async def test_issue_token_pair_raises_authentication_error(self) -> None:
        client = MagicMock()
        client.auth.sign_in_with_password.side_effect = AuthApiError(
            "Invalid login credentials", 400, "invalid_credentials"
        )

        sut = SupabaseTokenPairIssuer(client, access_token_expiry_s=3600)

        with pytest.raises(AuthenticationError):
            await sut.issue_token_pair(
                Email("test@example.com"), RawPassword("wrong-password")
            )


class TestSupabaseTokenPairRefresher:
    @pytest.mark.asyncio
    async def test_refresh_returns_new_token_pair(self) -> None:
        client = MagicMock()
        mock_session = Mock()
        mock_session.access_token = "new-access"  # noqa: S105
        mock_session.refresh_token = "new-refresh"  # noqa: S105
        mock_response = Mock()
        mock_response.session = mock_session
        client.auth.refresh_session.return_value = mock_response

        sut = SupabaseTokenPairRefresher(client, access_token_expiry_s=3600)
        access, refresh = await sut.refresh("old-refresh")

        assert access == "new-access"
        assert refresh == "new-refresh"

    @pytest.mark.asyncio
    async def test_refresh_raises_expired_error(self) -> None:
        client = MagicMock()
        client.auth.refresh_session.side_effect = AuthApiError(
            "Token expired", 401, "flow_state_expired"
        )

        sut = SupabaseTokenPairRefresher(client, access_token_expiry_s=3600)

        with pytest.raises(RefreshTokenExpiredError):
            await sut.refresh("expired-token")

    @pytest.mark.asyncio
    async def test_refresh_raises_not_found_error(self) -> None:
        client = MagicMock()
        client.auth.refresh_session.side_effect = AuthApiError(
            "Invalid token", 401, "bad_jwt"
        )

        sut = SupabaseTokenPairRefresher(client, access_token_expiry_s=3600)

        with pytest.raises(RefreshTokenNotFoundError):
            await sut.refresh("invalid-token")


class TestSupabaseAccessRevoker:
    @pytest.mark.asyncio
    async def test_revoke_calls_admin_sign_out(self) -> None:
        client = MagicMock()
        account_id = AccountId(UUID("00000000-0000-0000-0000-000000000001"))

        sut = SupabaseAccessRevoker(client)
        await sut.remove_all_account_access(account_id)

        client.auth.admin.sign_out.assert_called_once_with(
            str(account_id.value), scope="global"
        )

    @pytest.mark.asyncio
    async def test_revoke_swallows_auth_api_error(self) -> None:
        client = MagicMock()
        client.auth.admin.sign_out.side_effect = AuthApiError(
            "error", 500, "unexpected_failure"
        )
        account_id = AccountId(UUID("00000000-0000-0000-0000-000000000001"))

        sut = SupabaseAccessRevoker(client)
        await sut.remove_all_account_access(account_id)


class TestSupabasePasswordResetter:
    @pytest.mark.asyncio
    async def test_reset_password_calls_admin_update(self) -> None:
        client = MagicMock()
        account_id = AccountId(UUID("00000000-0000-0000-0000-000000000001"))

        sut = SupabasePasswordResetter(client)
        await sut.reset_password(account_id, RawPassword("new-password"))

        client.auth.admin.update_user_by_id.assert_called_once_with(
            str(account_id.value),
            {"password": "new-password"},
        )
