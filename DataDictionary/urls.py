from django.conf.urls import url
from DataDictionart.views import ShowDocModel

urlpatterns = [
    url(r'^show$', ShowDocModel.as_view()),
]