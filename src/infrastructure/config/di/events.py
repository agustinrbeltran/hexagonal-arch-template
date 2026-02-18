from dishka import Provider, Scope, provide_all

from infrastructure.events.handlers.user_handlers import LogUserCreated


class EventHandlerProvider(Provider):
    scope = Scope.REQUEST

    log_user_created = provide_all(LogUserCreated)
