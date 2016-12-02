from django.conf.urls import url
from .views import RoutePlanner

urlpatterns = [
    url(
        r'^calculate/(?P<pUserId>[0-9a-z-]+)/(?P<pOrigin>.+)/(?P<pDestination>.+)/(?P<language>\w+)$',
        RoutePlanner.as_view()),
    # without lang
    url(
        r'^calculate/(?P<pUserId>[0-9a-z-]+)/(?P<pOrigin>.+)/(?P<pDestination>.+)$',
        RoutePlanner.as_view()),
]
