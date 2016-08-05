from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^busStopInfo/(?P<pSecretKey>\w+)/(?P<pBusStop>\w+)$', views.busStopInfo),
]
