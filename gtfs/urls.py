from django.conf.urls import url
from gtfs.views import GTFSVersion

app_name = "gtfs"
urlpatterns = [
    url(r'^version$', GTFSVersion.as_view(), name="version"),
]
