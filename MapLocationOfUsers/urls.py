from django.conf.urls import url
from MapLocationOfUsers.views import MapHandler, GetMapPositions, GetMapTrajectory, GetGamificationUsersByDay

app_name = "map"
urlpatterns = [
    url(r'^show$', MapHandler.as_view(), name="show"),
    url(r'^activeuserpose$', GetMapPositions.as_view(), name="activeuserpose"),
    url(r'^activetrajectory$', GetMapTrajectory.as_view(), name="activetrajectory"),
    url(r'^gamificatedusersbyday$', GetGamificationUsersByDay.as_view(), name="gamificatedusersbyday$"),
]
