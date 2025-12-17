from dishka import Provider, Scope, from_context, provide

from setup.config.database import PostgresSettings, SqlaEngineSettings
from setup.config.logs import LoggingSettings
from setup.config.security import SecuritySettings
from setup.config.settings import AppSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    settings = from_context(AppSettings)

    @provide
    def postgres(self, settings: AppSettings) -> PostgresSettings:
        return settings.postgres

    @provide
    def sqla_engine(self, settings: AppSettings) -> SqlaEngineSettings:
        return settings.sqla

    @provide
    def security(self, settings: AppSettings) -> SecuritySettings:
        return settings.security

    @provide
    def logs(self, settings: AppSettings) -> LoggingSettings:
        return settings.logs
