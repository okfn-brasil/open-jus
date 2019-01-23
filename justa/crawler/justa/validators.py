from schematics.models import Model
from schematics.types import DateType, StringType


class JustaItemModel(Model):
    number = StringType(required=True)
    name = StringType(required=True)
    date = DateType(required=True)
    text = StringType(required=True)
    body = StringType()
