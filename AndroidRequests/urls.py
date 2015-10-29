from django.conf.urls import include, url
from . import views

from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.EventsByBus import EventsByBus

urlpatterns = [
	url(r'^nearbyBuses/(?P<pBusStop>\w+)$', views.nearbyBuses),
    url(r'^userPosition/(?P<pLat>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon>[\-+]?[0-9]*\.?[0-9]*)$', views.userPosition),
    url(r'^requestToken/(?P<pBusService>[0-9,\w]*)/(?P<pRegistrationPlate>[0-9,\w]*)$', RequestToken.as_view()),
    url(r'^endRoute/(?P<pToken>[0-9,a-f]{128})$', EndRoute.as_view()),
    url(r'^sendTrajectory/(?P<pToken>[0-9,a-f]{128})/(?P<pTrajectory>.*)$', SendPoses.as_view()),
    url(r'^reportEventBus/(?P<pBusService>[\w,0-9]*)/(?P<pBusPlate>[\w,0-9]*)/(?P<pTimeStamp>.*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBus.as_view()),
    url(r'^reportEventBusStop/(?P<pBusStopCode>[\w,0-9]*)/(?P<pTimeStamp>.*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBusStop.as_view()),
    url(r'^requestEventsForBus/(?P<pRegistrationPlate>[\w,0-9]*)$', EventsByBus.as_view()),
]