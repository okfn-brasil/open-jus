from datetime import date

import pytest
from django.db.utils import IntegrityError

from justa.core.models import CourtOrderTJSP


DATA = dict(
    source='tjsp',
    number='0001059-72.2013.8.26.0000',
    decision_date=date(1970, 1, 1),
    decision='Here comes the full text',
    status='Closed',
    source_numbers='42',
    reporter='Joanne Doe',
    category='Mono',
    petitioner='John',
    requested='Doe'
)


@pytest.mark.django_db
def test_complete_court_order():
    assert CourtOrderTJSP.objects.count() == 0
    CourtOrderTJSP.objects.create(**DATA)
    assert CourtOrderTJSP.objects.count() == 1


@pytest.mark.django_db
def test_court_order_without_optional_fields():
    assert CourtOrderTJSP.objects.count() == 0
    optional = (
        'status',
        'source_numbers',
        'reporter',
        'category',
        'petitioner',
        'requested'
    )
    for index, field in enumerate(optional):
        data = {key: value for key, value in DATA.items() if key is not field}
        data['number'] = data['number'][:-1] + str(index)
        CourtOrderTJSP.objects.create(**data)
    assert CourtOrderTJSP.objects.count() == len(optional)


@pytest.mark.django_db
def test_court_order_without_required_fields():
    data = {
        key: value for key, value in DATA.items()
        if key is not 'decision_date'
    }  # IntegrityError does not happen for text fields
    with pytest.raises(IntegrityError):
        CourtOrderTJSP.objects.create(**data)


@pytest.mark.django_db
def test_repeated_court_order():
    CourtOrderTJSP.objects.create(**DATA)
    with pytest.raises(IntegrityError):
        CourtOrderTJSP.objects.create(**DATA)
