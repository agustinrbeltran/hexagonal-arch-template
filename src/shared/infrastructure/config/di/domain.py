from dishka import Provider, Scope, provide

from core.domain.profile.ports import ProfileIdGenerator
from core.infrastructure.security.profile_id_generator import UuidProfileIdGenerator


class CoreDomainProvider(Provider):
    scope = Scope.APP

    profile_id_generator = provide(UuidProfileIdGenerator, provides=ProfileIdGenerator)
