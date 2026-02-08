from abc import ABC, abstractmethod

from application.create_user.command import CreateUserCommand, CreateUserResponse


class CreateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateUserCommand) -> CreateUserResponse: ...
