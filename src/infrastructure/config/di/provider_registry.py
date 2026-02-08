from collections.abc import Iterable

from dishka import Provider

from infrastructure.config.di.application import ApplicationProvider
from infrastructure.config.di.domain import DomainProvider
from infrastructure.config.di.infrastructure import infrastructure_providers
from infrastructure.config.di.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        DomainProvider(),
        ApplicationProvider(),
        *infrastructure_providers(),
        SettingsProvider(),
    )
