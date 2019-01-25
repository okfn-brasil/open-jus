from urllib.parse import urlparse

from decouple import config
from peewee import PostgresqlDatabase, SqliteDatabase


def _database():
    parsed = urlparse(config('DATABASE_URL'))
    if parsed.scheme == 'sqlite':
        return SqliteDatabase(parsed.path[1:])  # skip first slash

    return PostgresqlDatabase(
        parsed.path[1:],  # skip first slash
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port
    )


database = _database()
