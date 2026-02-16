from pydantic import BaseModel

from infrastructure.config.settings.database import PostgresSettings, SqlaEngineSettings
from infrastructure.config.settings.loader import (
    ValidEnvs,
    get_current_env,
    load_full_config,
)
from infrastructure.config.settings.logs import LoggingSettings
from infrastructure.config.settings.security import SecuritySettings


class AppSettings(BaseModel):
    postgres: PostgresSettings
    sqla: SqlaEngineSettings
    security: SecuritySettings
    logs: LoggingSettings


def load_settings(env: ValidEnvs | None = None) -> AppSettings:
    if env is None:
        env = get_current_env()
    raw_config = load_full_config(env=env)
    return AppSettings.model_validate(raw_config)
