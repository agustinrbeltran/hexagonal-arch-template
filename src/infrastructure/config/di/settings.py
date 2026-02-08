from dishka import Provider, Scope, from_context, provide

from infrastructure.config.settings.app_settings import AppSettings
from infrastructure.config.settings.database import PostgresSettings, SqlaEngineSettings
from infrastructure.config.settings.logs import LoggingSettings
from infrastructure.config.settings.security import SecuritySettings


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
