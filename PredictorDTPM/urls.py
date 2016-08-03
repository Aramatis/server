from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^busStopInfo/(?P<pBusStop>\w+)$', views.busStopInfo),
]
