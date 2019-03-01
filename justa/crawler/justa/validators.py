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


class CourtOrderTJSPModel(Model):
    number = StringType(required=True)
    decision = StringType(required=True)
    decision_date = DateType(required=True)
    status = StringType()
    source_numbers = StringType()
    reporter = StringType()
    category = StringType()
    subject = StringType()
    petitioner = StringType()
    petitioner_attorneys = StringType()
    requested = StringType()
    requested_attorneys = StringType()
    appeals = StringType()
