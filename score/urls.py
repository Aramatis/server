from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStop>\w+)$',        views.nearbyBuses),
    url(r'^registerReport$', RegisterReport.as_view()),
]
