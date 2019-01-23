from django.urls import path, include

from justa.core.views import CourtOrderResource


app_name = 'api'
urlpatterns = [
    path(
        'court-orders/',
        include(CourtOrderResource.urls(name_prefix='court_order'))
    ),
]
