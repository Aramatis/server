from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from maplocationofusers.views import MapHandler, GetMapPositions, GetMapTrajectory, GetGamificationUsersByDay

app_name = "map"
urlpatterns = [
    url(r'^show$', login_required(MapHandler.as_view()), name="show"),
    url(r'^activeuserpose$', login_required(GetMapPositions.as_view()), name="activeuserpose"),
    url(r'^activetrajectory$', login_required(GetMapTrajectory.as_view()), name="activetrajectory"),
    url(r'^gamificatedusersbyday$', login_required(GetGamificationUsersByDay.as_view()), name="gamificatedusersbyday"),
]
