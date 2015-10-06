from django.conf.urls import include, url
from . import views
from AndroidRequests.views import RequestToken, EndRoute, SendPoses
urlpatterns = [
	url(r'^nearbyBuses/(?P<pBusStop>\w+)$', views.nearbyBuses),
    url(r'^nearbyBusStops/(?P<pLat>[-+]?[0-9]*\.?[0-9]*)/(?P<pLon>[-+]?[0-9]*\.?[0-9]*)$', views.nearbyBusStops),
    url(r'^requestToken$', RequestToken.as_view()),
    url(r'^endRoute/(?P<pToken>[0-9,a-f]{128})$', EndRoute.as_view()),
    url(r'^sendTrajectoy/(?P<pToken>[0-9,a-f]{128})/(?P<pTrajectory>.*)$', SendPoses.as_view()),
]