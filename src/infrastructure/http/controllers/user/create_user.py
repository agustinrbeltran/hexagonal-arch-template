from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from application.create_user.command import CreateUserCommand, CreateUserResponse
from application.create_user.port import CreateUserUseCase
from domain.shared.errors import (
    AuthenticationError,
    AuthorizationError,
    DomainTypeError,
)
from domain.user.enums import UserRole
from domain.user.errors import (
    RoleAssignmentNotPermittedError,
    UsernameAlreadyExistsError,
)
from infrastructure.http.errors.callbacks import log_error, log_info
from infrastructure.http.errors.translators import ServiceUnavailableTranslator
from infrastructure.http.middleware.openapi_marker import bearer_scheme
from infrastructure.persistence.errors import DataMapperError
from infrastructure.security.errors import PasswordHasherBusyError


class CreateUserRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)
    username: str
    password: str
    role: UserRole = Field(default=UserRole.USER)


def create_create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateUserUseCase),
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
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def create_user(
        request_data_pydantic: CreateUserRequestPydantic,
        use_case: FromDishka[CreateUserUseCase],
    ) -> CreateUserResponse:
        request_data = CreateUserCommand(
            username=request_data_pydantic.username,
            password=request_data_pydantic.password,
            role=request_data_pydantic.role,
        )
        return await use_case.execute(request_data)

    return router
