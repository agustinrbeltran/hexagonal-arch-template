from dishka import Provider, Scope, provide, provide_all

from common.adapter.types_ import HasherThreadPoolExecutor, HasherSemaphore
from features.user.adapter.password_hasher_bcrypt import BcryptPasswordHasher
from features.user.adapter.utils.user_id_generator_uuid import \
    UuidUserIdGenerator
from features.user.domain.core.service.user_service import UserService
from features.user.domain.port.outbound.password_hasher import PasswordHasher
from features.user.domain.port.outbound.user_id_generator import UserIdGenerator

from setup.config.security import SecuritySettings


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
