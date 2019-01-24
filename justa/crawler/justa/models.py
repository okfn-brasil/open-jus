from functools import lru_cache
from urllib.parse import urlparse

from decouple import config
from peewee import CharField, DateField, Model, PostgresqlDatabase, SqliteDatabase


@lru_cache(maxsize=1)
def database():
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


class CourtOrder(Model):
    source = CharField(max_length=16)
    number = CharField(max_length=32)
    name = CharField(max_length=128)
    date = DateField()
    body = CharField(max_length=255, default='')
    text = CharField(max_length=255)

    class Meta:
        database = database()
        table_name = 'core_courtorder'  # table name as Django default
