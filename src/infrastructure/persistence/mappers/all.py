"""
Ensures imperative SQLAlchemy mappings are initialized at application startup.
Call the `map_tables` function in the application factory to initialize
mappings at startup.
"""

from infrastructure.persistence.mappers.auth_session import map_auth_sessions_table
from infrastructure.persistence.mappers.user import map_users_table


def map_tables() -> None:
    map_users_table()
    map_auth_sessions_table()
