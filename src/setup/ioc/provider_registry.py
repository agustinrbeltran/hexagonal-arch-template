from collections.abc import Iterable

from dishka import Provider

from setup.ioc.application import ApplicationProvider
from setup.ioc.domain import DomainProvider
from setup.ioc.infrastructure import infrastructure_providers
from setup.ioc.presentation import PresentationProvider
from setup.ioc.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        DomainProvider(),
        ApplicationProvider(),
        *infrastructure_providers(),
        PresentationProvider(),
        SettingsProvider(),
    )
