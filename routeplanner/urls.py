from django.conf.urls import url
from .views import RoutePlanner

urlpatterns = [
    url(r'^calculate/(?P<origin>.+)/(?P<destination>.+)/(?P<language>\w+)$', RoutePlanner.as_view()),
    # without lang
    url(r'^calculate/(?P<origin>.+)/(?P<destination>.+)$', RoutePlanner.as_view()),
]
