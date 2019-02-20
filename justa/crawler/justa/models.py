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


class CourtOrderTJSP(Model):
    source = CharField(max_length=16)
    number = CharField(max_length=255)
    decision = TextField()
    decision_date = DateField()
    status = TextField(default='')
    source_numbers = TextField(default='')
    reporter = TextField(default='')
    category = TextField(default='')
    petitioner = TextField(default='')
    requested = TextField(default='')

    class Meta:
        database = database
        table_name = 'core_courtordertjsp'  # table name as Django default
