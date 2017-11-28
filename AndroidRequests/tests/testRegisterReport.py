from django.test import TestCase

from AndroidRequests.models import Report
from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.statusResponse import Status

import base64
import os


class RegisterReportV1TestCase(TestCase):
    """ test for register report view """

    def setUp(self):
        # inputs
        self.phone_id = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.textMessage = 'this is a comment for testing purpose'
        with open(os.path.join(os.path.dirname(__file__), 'registerReportTestImage.jpg')) as imageFile:
            self.image = base64.b64encode(imageFile.read())
        self.formatImage = 'JPEG'
        self.reportInfo = 'additional info'
        self.userId = None
        self.sessionToken = None

        self.helper = TestHelper(self)

    def tearDown(self):
        """ delete image file saved """
        try:
            report = Report.objects.get(phoneId=self.phone_id)
            if report.imageFile is not None:
                report.imageFile.delete()
        except Report.DoesNotExist:
            pass

    def test_send_report_with_all_data(self):
        json_response = self.helper.report(self.textMessage, self.image, self.formatImage, self.phone_id,
                                           self.reportInfo)
        self.assertTrue(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_without_text(self):
        json_response = self.helper.report("", self.image, self.formatImage, self.phone_id, self.reportInfo)
        self.assertFalse(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_image(self):
        json_response = self.helper.report(self.textMessage, "", self.formatImage, self.phone_id, self.reportInfo)
        self.assertTrue(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_without_image_and_without_extension(self):
        json_response = self.helper.report(self.textMessage, "", "", self.phone_id, self.reportInfo)
        self.assertTrue(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_with_image_but_without_extension(self):
        json_response = self.helper.report(self.textMessage, self.image, "", self.phone_id, self.reportInfo)
        self.assertFalse(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_with_image_but_with_invalid_extension(self):
        wrong_extension = 'JPPNG'
        json_response = self.helper.report(self.textMessage, self.image, wrong_extension, self.phone_id,
                                           self.reportInfo)
        self.assertFalse(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_user_id(self):
        json_response = self.helper.report(self.textMessage, self.image, self.formatImage, "", self.reportInfo)
        self.assertFalse(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_additional_info(self):
        json_response = self.helper.report(self.textMessage, self.image, self.formatImage, self.phone_id, "")
        self.assertTrue(json_response['valid'])
        self.assertEqual(Report.objects.all().count(), 1)


class RegisterReportV2TestCase(TestCase):
    """ test for register report view """

    def setUp(self):
        # inputs
        self.phone_id = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.textMessage = 'this is a comment for testing purpose'
        with open(os.path.join(os.path.dirname(__file__), 'registerReportTestImage.jpg')) as imageFile:
            self.image = base64.b64encode(imageFile.read())
        self.formatImage = 'JPEG'
        self.reportInfo = 'additional info'

        # create user
        self.helper = TestHelper(self)
        user = self.helper.createTranSappUsers(1)[0]

        self.userId = user.userId
        self.sessionToken = user.sessionToken

    def tearDown(self):
        """ delete image file saved """
        try:
            report = Report.objects.get(phoneId=self.phone_id)
            if report.imageFile is not None:
                report.imageFile.delete()
        except Report.DoesNotExist:
            pass

    def test_send_report_with_all_data(self):
        json_response = self.helper.reportV2(self.textMessage, self.image, self.formatImage, self.phone_id,
                                             self.reportInfo, self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_with_all_data_but_without_user(self):
        json_response = self.helper.reportV2(self.textMessage, self.image, self.formatImage, self.phone_id,
                                             self.reportInfo)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_without_text(self):
        json_response = self.helper.reportV2("", self.image, self.formatImage, self.phone_id, self.reportInfo,
                                             self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.REPORT_CAN_NOT_BE_SAVED, {})['status'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_image(self):
        json_response = self.helper.reportV2(self.textMessage, "", self.formatImage, self.phone_id, self.reportInfo,
                                             self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_without_image_and_without_extension(self):
        json_response = self.helper.reportV2(self.textMessage, "", "", self.phone_id, self.reportInfo, self.userId,
                                             self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(Report.objects.all().count(), 1)

    def test_send_report_with_image_but_without_extension(self):
        json_response = self.helper.reportV2(self.textMessage, self.image, "", self.phone_id, self.reportInfo,
                                             self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.REPORT_CAN_NOT_BE_SAVED, {})['status'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_with_image_but_with_invalid_extension(self):
        wrong_extension = 'JPPNG'
        json_response = self.helper.reportV2(self.textMessage, self.image, wrong_extension, self.phone_id,
                                             self.reportInfo, self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.REPORT_CAN_NOT_BE_SAVED, {})['status'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_user_id(self):
        json_response = self.helper.reportV2(self.textMessage, self.image, self.formatImage, "", self.reportInfo,
                                             self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.REPORT_CAN_NOT_BE_SAVED, {})['status'])
        self.assertEqual(Report.objects.all().count(), 0)

    def test_send_report_without_additional_info(self):
        json_response = self.helper.reportV2(self.textMessage, self.image, self.formatImage, self.phone_id, "",
                                             self.userId, self.sessionToken)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(Report.objects.all().count(), 1)
