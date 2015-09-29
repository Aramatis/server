from django.conf.urls import url
from MapLocationOfUsers.views import MapHandler, GetMapPositions

urlpatterns = [
	url(r'^show$', MapHandler.as_view()),
	url(r'^activeuserpose$', GetMapPositions.as_view()),
]