from django.urls import path, include

from justa.core.views import CourtOrderResource, CourtOrderTJSPResource


app_name = 'api'
urlpatterns = [
    path(
        'court-orders/',
        include(CourtOrderResource.urls(name_prefix='court_order'))
    ),
    path(
        'court-orders-tjsp/',
        include(CourtOrderTJSPResource.urls(name_prefix='court_order_tjsp'))
    ),
]
