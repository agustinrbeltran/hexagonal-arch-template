from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from account.application.create_account.command import (
    CreateAccountCommand,
    CreateAccountResponse,
)
from account.application.create_account.port import CreateAccountUseCase
from account.domain.account.enums import AccountRole
from account.domain.account.errors import (
    EmailAlreadyExistsError,
    RoleAssignmentNotPermittedError,
)
from account.infrastructure.security.errors import PasswordHasherBusyError
from shared.domain.errors import (
    AuthenticationError,
    AuthorizationError,
    DomainTypeError,
)
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.infrastructure.persistence.errors import DataMapperError


class CreateAccountRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)
    email: str
    password: str
    role: AccountRole = Field(default=AccountRole.USER)


def create_create_account_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateAccountUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def create_account(
        request_data_pydantic: CreateAccountRequestPydantic,
        use_case: FromDishka[CreateAccountUseCase],
    ) -> CreateAccountResponse:
        request_data = CreateAccountCommand(
            email=request_data_pydantic.email,
            password=request_data_pydantic.password,
            role=request_data_pydantic.role,
        )
        return await use_case.execute(request_data)

    return router
