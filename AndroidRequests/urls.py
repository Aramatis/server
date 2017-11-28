from django.conf.urls import url

from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EvaluateTrip import EvaluateTrip
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RegisterEventBusV2 import RegisterEventBusV2
from AndroidRequests.allviews.RegisterReport import RegisterReport, RegisterReportV2
from AndroidRequests.allviews.RequestEventsToNotified import RequestEventsToNotified
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.allviews.RequestUUID import RequestUUID
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.SendPosesV2 import SendPosesV2
from AndroidRequests.allviews.ServiceRoute import ServiceRoute
from AndroidRequests.allviews.SetDirection import SetDirection
from AndroidRequests.allviews.UserRanking import UserRanking
from AndroidRequests.allviews.UserScoreSession import TranSappUserLogin
from AndroidRequests.allviews.UserScoreSession import TranSappUserLogout
from AndroidRequests.allviews.UserScoreSession import UpdateTranSappUserSettings
from . import views

urlpatterns = [
    url(r'^nearbyBuses/(?P<phone_id>[0-9a-z-]+)/(?P<stop_code>\w+)$',
        views.nearby_buses),
    url(r'^registerReport$', RegisterReport.as_view()),
    url(
        r'^userPosition/(?P<phone_id>[0-9a-z-]+)/(?P<latitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<longitude>[\-+]?[0-9]*\.?[0-9]*)$',
        views.save_user_position),
    url(
        r'^requestToken/(?P<phone_id>[0-9a-z-]+)/(?P<route>[0-9,\w]*)/(?P<license_plate>[0-9,\w,-]{6,8})$',
        RequestToken.as_view()),
    url(r'^endRoute/(?P<token>[0-9,a-f]{128})$', EndRoute.as_view()),
    url(r'^sendTrajectory$', SendPoses.as_view()),
    # reportEventBus with location
    url(
        r'^reportEventBus/(?P<phone_id>[0-9a-z-]+)/(?P<route>[\w,0-9]*)/(?P<license_plate>[\w,0-9,-]*)/(?P<event_id>evn\d{5})/(?P<latitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<longitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBus.as_view()),
    # reportEventBus without location
    url(
        r'^reportEventBus/(?P<phone_id>[0-9a-z-]+)/(?P<route>[\w,0-9]*)/(?P<license_plate>[\w,0-9,-]*)/(?P<event_id>evn\d{5})/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBus.as_view()),
    url(
        r'^reportEventBusStop/(?P<phone_id>[0-9a-z-]+)/(?P<stop_code>[\w,0-9]*)/(?P<event_id>evn\d{5})/(?P<latitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<longitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBusStop.as_view()),
    url(
        r'^reportEventBusStop/(?P<phone_id>[0-9a-z-]+)/(?P<stop_code>[\w,0-9]*)/(?P<event_id>evn\d{5})/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBusStop.as_view()),
    url(
        r'^reportEventBusStop/(?P<phone_id>[0-9a-z-]+)/(?P<stop_code>[\w,0-9]*)/(?P<route>[0-9,\w]*)/(?P<event_id>evn\d{5})/(?P<latitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<longitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBusStop.as_view()),
    url(
        r'^reportEventBusStop/(?P<phone_id>[0-9a-z-]+)/(?P<stop_code>[\w,0-9]*)/(?P<route>[0-9,\w]*)/(?P<event_id>evn\d{5})/(?P<confirm_or_decline>(confirm|decline))$',
        RegisterEventBusStop.as_view()),
 
    # List of events that depend of parameter pWhich={stopstop,stopbus, busbus}
    url(r'^requestEventsToNotified/(?P<which>[\w,0-9]*)$',
        RequestEventsToNotified.as_view()),
    # List of bus events
    url(
        r'^requestEventsForBus/(?P<license_plate>[\w,0-9,-]{6,8})/(?P<route>[\w,0-9]*)$',
        EventsByBus.as_view()),
    # List of bus stop events
    url(
        r'^requestEventsForBusStop/(?P<stop_code>[\w,0-9]*)$',
        EventsByBusStop.as_view()),
    # List of bus stop of a service
    url(
        r'^requestBusStopsForService/(?P<route>[\w,0-9]*)$',
        BusStopsByService.as_view()),
    url(
        r'^requestRouteForService/(?P<pBusService>[\w,0-9]*)/(?P<pLat1>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon1>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLat2>[\-+]?[0-9]*\.?[0-9]*)/(?P<pLon2>[\-+]?[0-9]*\.?[0-9]*)$',
        ServiceRoute.as_view()),
    # setDirection receives parameter by POST
    url(r'^setDirection$', SetDirection.as_view()),
    url(r'^getUUID/(?P<license_plate>[\w,0-9,-]{6,8})$',
        RequestUUID.as_view()),
    # =====================================================
    # VERSION 2
    # =====================================================
    url(
        r'^requestToken/v2/(?P<phone_id>[0-9a-z-]+)/(?P<route>[0-9,\w]*)/(?P<machine_id>[0-9a-z-]+)$',
        RequestTokenV2.as_view()),
    url(
        r'^reportEventBus/v2/(?P<phone_id>[0-9a-z-]+)/(?P<machine_id>[0-9a-z-]+)/(?P<route>[\w,0-9]*)/(?P<event_id>.*)/(?P<latitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<longitude>[\-+]?[0-9]*\.?[0-9]*)/(?P<confirm_or_decline>.*)$',
        RegisterEventBusV2.as_view()),
    url(
        r'^reportEventBus/v2/(?P<phone_id>[0-9a-z-]+)/(?P<machine_id>[0-9a-z-]+)/(?P<route>[\w,0-9]*)/(?P<event_id>.*)/(?P<confirm_or_decline>.*)$',
        RegisterEventBusV2.as_view()),
    url(r'^requestEventsForBus/v2/(?P<machine_id>[0-9a-z-]+)$',
        EventsByBusV2.as_view()),

    # =====================================================
    # SCORE SESSION
    # =====================================================
    url(r'^login$', TranSappUserLogin.as_view()),
    url(r'^logout$', TranSappUserLogout.as_view()),
    url(r'^updateUserSettings$', UpdateTranSappUserSettings.as_view()),
    url(r'^getRanking$', UserRanking.as_view()),
    # =====================================================
    # EVALUATE TRIP
    # =====================================================
    url(r'^evaluateTrip$', EvaluateTrip.as_view()),
    url(r'^reportEventBus/v2$', RegisterEventBusV2.as_view()),
    url(r'^reportEventBusStop$', RegisterEventBusStop.as_view()),
    # =====================================================
    # GET IN THE BUS   
    # =====================================================
    url(r'^requestToken/v2$', RequestTokenV2.as_view()),
    url(r'^sendTrajectory/v2$', SendPosesV2.as_view()),
    url(r'^endRoute$', EndRoute.as_view()),
    # =====================================================
    # reports
    # =====================================================
    url(r'^registerReport/v2$', RegisterReportV2.as_view()),
]
