import base64
# python stuf
import json
import os

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.test import TestCase, RequestFactory

# views
from AndroidRequests.allviews.RegisterReport import RegisterReport
# model
from AndroidRequests.models import Report


class RegisterReportTestCase(TestCase):
    """ test for register report view """

    def setUp(self):

        self.factory = RequestFactory()

        self.request = self.factory.post('/android/registerReport/')
        self.request.user = AnonymousUser()
        self.reponseView = RegisterReport()

        # inputs
        self.phoneId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.textMessage = 'this is a comment for testing purpose'
        with open(os.path.join(os.path.dirname(__file__), 'registerReportTestImage.jpg')) as imageFile:
            self.image = base64.b64encode(imageFile.read())
        self.formatImage = 'JPEG'
        self.reportInfo = 'additional info'

        POST = {'text': self.textMessage, 'img': self.image, 'ext': self.formatImage, 'userId': self.phoneId,
                'report_info': self.reportInfo}

        self.request.POST = POST

    def test_send_report_with_all_data(self):
        request = self.request

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertTrue(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

        # delete image file saved
        report = Report.objects.get(phoneId=self.phoneId)
        path = os.path.join(settings.MEDIA_IMAGE, report.imageName)
        os.remove(path)

    def test_send_report_without_text(self):
        request = self.request
        request.POST.pop('text')

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertFalse(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_image(self):
        request = self.request
        request.POST.pop('img')

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertTrue(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_without_image_and_without_extension(self):
        request = self.request
        request.POST.pop('img')
        request.POST.pop('ext')

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertTrue(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_with_image_but_without_extension(self):
        request = self.request
        request.POST.pop('ext')

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertFalse(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_with_image_but_with_invalid_extension(self):
        request = self.request
        request.POST['ext'] = 'JPPNG'

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertFalse(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_user_id(self):
        request = self.request
        request.POST.pop('userId')

        with transaction.atomic():
            response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertFalse(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_additional_info(self):
        request = self.request
        request.POST.pop('report_info')

        response = self.reponseView.post(request)
        jsonResponse = json.loads(response.content)

        self.assertTrue(jsonResponse['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

        # delete image file saved
        report = Report.objects.get(phoneId=self.phoneId)
        path = os.path.join(settings.MEDIA_IMAGE, report.imageName)
        os.remove(path)
