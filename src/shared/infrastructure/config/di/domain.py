from dishka import Provider, Scope, provide, provide_all

from account.domain.account.ports import AccountIdGenerator, PasswordHasher
from account.domain.account.services import AccountService
from account.infrastructure.security.account_id_generator import UuidAccountIdGenerator
from account.infrastructure.security.password_hasher_bcrypt import BcryptPasswordHasher
from core.domain.profile.ports import ProfileIdGenerator
from core.infrastructure.security.profile_id_generator import UuidProfileIdGenerator
from shared.infrastructure.config.settings.security import SecuritySettings
from shared.infrastructure.persistence.types_ import (
    HasherSemaphore,
    HasherThreadPoolExecutor,
)


class AccountDomainProvider(Provider):
    scope = Scope.APP

    # Services
    account_service = provide_all(AccountService)

    # Ports
    account_id_generator = provide(UuidAccountIdGenerator, provides=AccountIdGenerator)

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


class CoreDomainProvider(Provider):
    scope = Scope.APP

    profile_id_generator = provide(UuidProfileIdGenerator, provides=ProfileIdGenerator)
