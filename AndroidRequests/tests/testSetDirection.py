from django.test import TestCase, RequestFactory

# my stuff
from AndroidRequests.tests.testHelper import TestHelper
# views
import AndroidRequests.constants as Constants


class SetDirectionTest(TestCase):
    """ test for Setdirection url """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.service = '507'
        self.licencePlate = 'PABJ45'
        self.busStop = 'PA459'

        self.helper.insertServicesOnDatabase([self.service])
        self.helper.insertBusstopsOnDatabase([self.busStop])
        self.helper.insertServicesByBusstopsOnDatabase([self.busStop])

    def test_setDirectionWithActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has not been finished with dummy licence plate """

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], True)
            self.assertEqual(
                jsonResponse['message'],
                "User bus direction updated.")

        self.helper.endRoute(travelKey)

    def test_setDirectionWithActiveToken(self):
        """ set direction of travel has not been finished """

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], True)
            self.assertEqual(
                jsonResponse['message'],
                "User bus direction updated.")

        self.helper.endRoute(travelKey)

    def test_setDirectionWithoutActiveToken(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.endRoute(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Token doesn't exist.")

    def test_setDirectionWithoutActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.endRoute(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Token doesn't exist.")

    def test_setDirectionWithWrongDirection(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["Z", "S", "other things"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Invalid direction.")

        self.helper.endRoute(travelKey)
