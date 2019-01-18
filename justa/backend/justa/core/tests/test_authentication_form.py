import pytest

from justa.core.forms import AuthenticationForm


TOKEN = {'token': 'a1d0c6e83f027327d8461063f4ac58a6'}


@pytest.mark.django_db
def test_valid_token(settings):
    settings.SECRET_KEY = '42'
    form = AuthenticationForm(TOKEN)
    assert form.is_valid()


@pytest.mark.django_db
def test_invalid_token(settings):
    settings.SECRET_KEY = '42'
    form = AuthenticationForm({'token': 'not a valid token'})
    assert not form.is_valid()
