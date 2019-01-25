from peewee import CharField, DateField, Model, TextField

from justa.db import database


class CourtOrder(Model):
    source = CharField(max_length=16)
    number = CharField(max_length=64)
    name = CharField(max_length=128)
    date = DateField()
    body = CharField(max_length=255, default='')
    text = TextField()

    class Meta:
        database = database
        table_name = 'core_courtorder'  # table name as Django default
