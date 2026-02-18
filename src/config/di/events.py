from dishka import Provider, Scope, provide_all

from account.infrastructure.events.handlers.log_account_created import LogAccountCreated
from core.infrastructure.events.handlers.create_profile_on_account_created import (
    CreateProfileOnAccountCreated,
)


class EventHandlerProvider(Provider):
    scope = Scope.REQUEST

    log_account_created = provide_all(LogAccountCreated)
    create_profile_on_account_created = provide_all(CreateProfileOnAccountCreated)
