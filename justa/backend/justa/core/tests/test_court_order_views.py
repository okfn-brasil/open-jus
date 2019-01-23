import pytest
from django.shortcuts import resolve_url
from mixer.backend.django import mixer

from justa.core.models import CourtOrder


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
def test_list(client):
    orders = mixer.cycle(3).blend(CourtOrder)
    resp = client.get(resolve_url('api:court_order_list'))
    assert resp.status_code == 200
    for order in orders:
        assert order.name in resp.content.decode('utf-8')


@pytest.mark.django_db
def test_detail(client):
    order = mixer.blend(CourtOrder)
    resp = client.get(resolve_url('api:court_order_detail', pk=order.pk))
    assert resp.status_code == 200
    assert order.name in resp.content.decode('utf-8')


@pytest.mark.django_db
def test_create(client, settings):
    settings.SECRET_KEY = '42'
    assert CourtOrder.objects.count() == 0
    url = resolve_url('api:court_order_list')
    resp = client.post(url, DATA, content_type='application/json')
    assert resp.status_code == 201
    assert CourtOrder.objects.count() == 1
    assert 'John Doe' in resp.content.decode('utf-8')
