from django.conf.urls import url
from DataDictionary.views import ShowDocModel

urlpatterns = [
    url(r'^show$', ShowDocModel.as_view()),
]