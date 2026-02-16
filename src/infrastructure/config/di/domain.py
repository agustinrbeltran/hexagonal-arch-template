from dishka import Provider, Scope, provide, provide_all

from domain.user.ports import PasswordHasher, UserIdGenerator
from domain.user.services import UserService
from infrastructure.config.settings.security import SecuritySettings
from infrastructure.persistence.types_ import HasherSemaphore, HasherThreadPoolExecutor
from infrastructure.security.password_hasher_bcrypt import BcryptPasswordHasher
from infrastructure.security.user_id_generator_uuid import UuidUserIdGenerator


class DomainProvider(Provider):
    scope = Scope.APP

    # Services
    user_service = provide_all(
        UserService,
    )

    # Ports
    user_id_generator = provide(UuidUserIdGenerator, provides=UserIdGenerator)

    @provide
    def provide_password_hasher(
        self,
        security: SecuritySettings,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
    ) -> PasswordHasher:
        return BcryptPasswordHasher(
            pepper=security.password.pepper.encode(),
            work_factor=security.password.hasher_work_factor,
            executor=executor,
            semaphore=semaphore,
            semaphore_wait_timeout_s=security.password.hasher_semaphore_wait_timeout_s,
        )
