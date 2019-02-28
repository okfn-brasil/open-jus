from django.urls import path, include

from justa.core.views import CourtOrderResource, CourtOrderESAJResource


app_name = 'api'
urlpatterns = [
    path(
        'court-orders/',
        include(CourtOrderResource.urls(name_prefix='court_order'))
    ),
    path(
        'court-orders-esaj/',
        include(CourtOrderESAJResource.urls(name_prefix='court_order_esaj'))
    ),
]
