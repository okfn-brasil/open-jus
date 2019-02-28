import pytest
from django.shortcuts import resolve_url
from mixer.backend.django import mixer

from justa.core.models import CourtOrderESAJ


@pytest.mark.django_db
def test_list(client):
    orders = mixer.cycle(3).blend(CourtOrderESAJ)
    resp = client.get(resolve_url('api:court_order_esaj_list'))
    assert resp.status_code == 200
    for order in orders:
        assert order.number.encode('utf-8') in resp.content


@pytest.mark.django_db
def test_detail(client):
    order = mixer.blend(CourtOrderESAJ)
    resp = client.get(resolve_url('api:court_order_esaj_detail', pk=order.pk))
    assert resp.status_code == 200
    assert order.number in resp.content.decode('utf-8')
