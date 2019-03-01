import pytest
from django.shortcuts import resolve_url
from mixer.backend.django import mixer

from justa.core.models import CourtOrderTJSP


@pytest.mark.django_db
def test_list(client):
    orders = mixer.cycle(3).blend(CourtOrderTJSP)
    resp = client.get(resolve_url('api:court_order_tjsp_list'))
    assert resp.status_code == 200
    for order in orders:
        assert order.number.encode('utf-8') in resp.content


@pytest.mark.django_db
def test_detail(client):
    order = mixer.blend(CourtOrderTJSP)
    resp = client.get(resolve_url('api:court_order_tjsp_detail', pk=order.pk))
    assert resp.status_code == 200
    assert order.number in resp.content.decode('utf-8')
