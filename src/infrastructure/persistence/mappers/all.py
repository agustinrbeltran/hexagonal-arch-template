"""
Ensures imperative SQLAlchemy mappings are initialized at application startup.
Call the `map_tables` function in the application factory to initialize
mappings at startup.
"""

from infrastructure.persistence.mappers.refresh_token import map_refresh_tokens_table
from infrastructure.persistence.mappers.user import map_users_table


def map_tables() -> None:
    map_users_table()
    map_refresh_tokens_table()
