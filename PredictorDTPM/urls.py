from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^nearbyBuses/(?P<pBusStop>\w+)$', views.nearbyBuses),
]
