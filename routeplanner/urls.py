from django.conf.urls import url
from .views import RoutePlanner

urlpatterns = [
    url(r'^calculate$', RoutePlanner.as_view()),
]
