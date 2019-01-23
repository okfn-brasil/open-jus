from datetime import date

import pytest
from django.db.utils import IntegrityError

from justa.core.models import CourtOrder


DATA = dict(
    number='42',
    name='John Doe',
    date=date(1970, 1, 1),
    text='Here comes the full text',
    body='Earth'
)


@pytest.mark.django_db
def test_complete_court_order():
    assert CourtOrder.objects.count() == 0
    CourtOrder.objects.create(**DATA)
    assert CourtOrder.objects.count() == 1


@pytest.mark.django_db
def test_court_order_without_body_and_text():
    assert CourtOrder.objects.count() == 0
    data = DATA.copy()
    del data['body']
    del data['text']
    CourtOrder.objects.create(**data)
    assert CourtOrder.objects.count() == 1


@pytest.mark.django_db
def test_court_order_without_required_fields():
    with pytest.raises(IntegrityError):
        CourtOrder.objects.create(body='Earth', text='The full text')


@pytest.mark.django_db
def test_repeated_court_order():
    CourtOrder.objects.create(**DATA)
    with pytest.raises(IntegrityError):
        CourtOrder.objects.create(**DATA)
