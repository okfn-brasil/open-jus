from schematics.models import Model
from schematics.types import DateType, StringType


class CourtOrderModel(Model):
    number = StringType(required=True)
    name = StringType(required=True)
    date = DateType(required=True)
    text = StringType(required=True)
    body = StringType()


class CourtOrderReferenceModel(Model):
    number = StringType(required=True)
    source = StringType(required=True)
