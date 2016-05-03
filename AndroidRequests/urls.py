from django.conf.urls import include, url
from . import views

from AndroidRequests.allviews.RequestToken import *
from AndroidRequests.allviews.EndRoute import *
from AndroidRequests.allviews.SendPoses import *
from AndroidRequests.allviews.RegisterEventBus import *
from AndroidRequests.allviews.RegisterEventBusStop import *
from AndroidRequests.allviews.EventsByBus import *
from AndroidRequests.allviews.RequestEventsToNotified import *
from AndroidRequests.allviews.EventsByBusStop import *
from AndroidRequests.allviews.BusStopsByService import *
from AndroidRequests.allviews.RegisterReport import *

urlpatterns = [
	url(r'^nearbyBuses/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStop>\w+)$', views.nearbyBuses),
    url(r'^registerReport/(?P<pUserId>[0-9a-z-]+)$', RegisterReport.as_view()),
    url(r'^userPosition/(?P<pUserId>[0-9a-z-]+)/(?P<pLat>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon>[\-+]?[0-9]*\.?[0-9]*)$', views.userPosition),
    url(r'^requestToken/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[0-9,\w]*)/(?P<pRegistrationPlate>[0-9,\w]*)$', RequestToken.as_view()),
    url(r'^endRoute/(?P<pUserId>[0-9a-z-]+)/(?P<pToken>[0-9,a-f]{128})$', EndRoute.as_view()),
    url(r'^sendTrajectory/(?P<pUserId>[0-9a-z-]+)/(?P<pToken>[0-9,a-f]{128})/(?P<pTrajectory>.*)$', SendPoses.as_view()),
    # reportEventBus with location
    url(r'^reportEventBus/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[\w,0-9]*)/(?P<pBusPlate>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pLatitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLongitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pConfirmDecline>.*)$', RegisterEventBus.as_view()),
    # reportEventBus without location
    url(r'^reportEventBus/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[\w,0-9]*)/(?P<pBusPlate>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBus.as_view()),
    url(r'^reportEventBusStop/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStopCode>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pLatitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLongitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pConfirmDecline>.*)$', RegisterEventBusStop.as_view()),
    url(r'^reportEventBusStop/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStopCode>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBusStop.as_view()),
    url(r'^requestEventsForBus/(?P<pUserId>[0-9a-z-]+)/(?P<pRegistrationPlate>[\w,0-9]*)/(?P<pBusService>[\w,0-9]*)$', EventsByBus.as_view()),
    url(r'^requestEventsToNotified/(?P<pUserId>[0-9a-z-]+)/(?P<pWhich>[\w,0-9]*)$', RequestEventsToNotified.as_view()),
    url(r'^requestEventsForBusStop/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStopCode>[\w,0-9]*)$', EventsByBusStop.as_view()),
    url(r'^requestBusStopsForService/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[\w,0-9]*)$', BusStopsByService.as_view()),
]
