from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^nearbyBuses/(?P<pBusStop>\w+)$', views.nearbyBuses),
    url(r'^nearbyBusStops/(?P<pLat>[-+]?[0-9]*\.?[0-9]*)/(?P<pLon>[-+]?[0-9]*\.?[0-9]*)$', views.nearbyBusStops),
]