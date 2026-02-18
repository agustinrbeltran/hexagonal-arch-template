from collections.abc import Iterable

from dishka import Provider

from shared.infrastructure.config.di.application import (
    AccountApplicationProvider,
    CoreApplicationProvider,
)
from shared.infrastructure.config.di.domain import (
    AccountDomainProvider,
    CoreDomainProvider,
)
from shared.infrastructure.config.di.events import EventHandlerProvider
from shared.infrastructure.config.di.infrastructure import infrastructure_providers
from shared.infrastructure.config.di.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        AccountDomainProvider(),
        CoreDomainProvider(),
        AccountApplicationProvider(),
        CoreApplicationProvider(),
        EventHandlerProvider(),
        *infrastructure_providers(),
        SettingsProvider(),
    )
