from django.conf.urls import url
from MapLocationOfUsers.views import MapHandler

urlpatterns = [
	url(r'^show$', MapHandler.as_view()),
]