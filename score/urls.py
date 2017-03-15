from django.conf.urls import url
from score.views import TranSappUserLogin, TranSappUserLogout

urlpatterns = [
    url(r'^login$', TranSappUserLogin.as_view()),
    url(r'^logout$', TranSappUserLogout.as_view()),
]
