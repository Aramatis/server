from django.conf.urls import url
from . import views

from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.RequestEventsToNotified import RequestEventsToNotified
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.RegisterReport import RegisterReport
from AndroidRequests.allviews.ServiceRoute import ServiceRoute

urlpatterns = [
    url(r'^nearbyBuses/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStop>\w+)$', views.nearbyBuses),
    url(r'^registerReport$', RegisterReport.as_view()),
    url(r'^userPosition/(?P<pUserId>[0-9a-z-]+)/(?P<pLat>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon>[\-+]?[0-9]*\.?[0-9]*)$', views.userPosition),
    url(r'^requestToken/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[0-9,\w]*)/(?P<pRegistrationPlate>[0-9,\w,-]{6,8})$', RequestToken.as_view()),
    url(r'^endRoute/(?P<pToken>[0-9,a-f]{128})$', EndRoute.as_view()),
    url(r'^sendTrajectory$', SendPoses.as_view()),
    # reportEventBus with location
    url(r'^reportEventBus/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[\w,0-9]*)/(?P<pBusPlate>[\w,0-9,-]*)/(?P<pEventID>.*)/(?P<pLatitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLongitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pConfirmDecline>.*)$', RegisterEventBus.as_view()),
    # reportEventBus without location
    url(r'^reportEventBus/(?P<pUserId>[0-9a-z-]+)/(?P<pBusService>[\w,0-9]*)/(?P<pBusPlate>[\w,0-9,-]*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBus.as_view()),
    url(r'^reportEventBusStop/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStopCode>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pLatitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLongitud>[\-+]?[0-9]*\.?[0-9]*)/(?P<pConfirmDecline>.*)$', RegisterEventBusStop.as_view()),
    url(r'^reportEventBusStop/(?P<pUserId>[0-9a-z-]+)/(?P<pBusStopCode>[\w,0-9]*)/(?P<pEventID>.*)/(?P<pConfirmDecline>.*)$', RegisterEventBusStop.as_view()),
    # List of events that depend of parameter pWhich={stopstop,stopbus, busbus}
    url(r'^requestEventsToNotified/(?P<pWhich>[\w,0-9]*)$', RequestEventsToNotified.as_view()),
    # List of bus events
    url(r'^requestEventsForBus/(?P<pRegistrationPlate>[\w,0-9,-]{6,8})/(?P<pBusService>[\w,0-9]*)$', EventsByBus.as_view()),
    # List of bus stop events
    url(r'^requestEventsForBusStop/(?P<pBusStopCode>[\w,0-9]*)$', EventsByBusStop.as_view()),
    # List of bus stop of a service
    url(r'^requestBusStopsForService/(?P<pBusService>[\w,0-9]*)$', BusStopsByService.as_view()),
    url(r'^requestRouteForService/(?P<pBusService>[\w,0-9]*)/(?P<pLat1>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon1>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLat2>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon2>[\-+]?[0-9]*\.?[0-9]*)$', ServiceRoute.as_view()),
]
