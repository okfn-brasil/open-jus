import pytest

from justa.core.forms import CourtOrderForm


DATA = dict(
    source='sc',
    number='42',
    name='John Doe',
    date='1970-12-31',
    text='Here comes the full text',
    body='Earth',
    token='a1d0c6e83f027327d8461063f4ac58a6'
)


@pytest.mark.django_db
def test_valid_form(settings):
    settings.SECRET_KEY = '42'
    form = CourtOrderForm(DATA)
    assert form.is_valid()


@pytest.mark.django_db
def test_form_with_missing_data(settings):
    settings.SECRET_KEY = '42'
    data = DATA.copy()
    del data['number']
    form = CourtOrderForm(data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_form_with_invalid_date(settings):
    settings.SECRET_KEY = '42'
    data = DATA.copy()
    data['date'] = 'not a date'
    form = CourtOrderForm(data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_form_with_invalid_token(settings):
    settings.SECRET_KEY = '42'
    data = DATA.copy()
    data['token'] = '42'
    form = CourtOrderForm(data)
    assert not form.is_valid()
