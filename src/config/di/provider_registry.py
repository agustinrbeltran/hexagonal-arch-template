from collections.abc import Iterable

from dishka import Provider

from config.di.application import (
    AccountApplicationProvider,
    CoreApplicationProvider,
)
from config.di.domain import AccountDomainProvider, CoreDomainProvider
from config.di.events import EventHandlerProvider
from config.di.infrastructure import infrastructure_providers
from config.di.settings import SettingsProvider


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
