from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.constants as Constants


class SetDirectionTest(TestCase):
    """ test for Setdirection url """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.service = '507'
        self.license_plate = 'PABJ45'
        self.busStop = 'PA459'

        self.helper.insertServicesOnDatabase([self.service])
        self.helper.insertBusstopsOnDatabase([self.busStop])
        self.helper.insertServicesByBusstopsOnDatabase([self.busStop])

    def test_setDirectionWithActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has not been finished with dummy licence plate """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        directions = ["I", "R"]
        for direction in directions:
            json_response = self.helper.setDirection(travel_key, direction)

            self.assertEqual(json_response['valid'], True)
            self.assertEqual(
                json_response['message'],
                "User bus direction updated.")

        self.helper.endRoute(travel_key)

    def test_setDirectionWithActiveToken(self):
        """ set direction of travel has not been finished """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, self.license_plate)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        directions = ["I", "R"]
        for direction in directions:
            json_response = self.helper.setDirection(travel_key, direction)

            self.assertEqual(json_response['valid'], True)
            self.assertEqual(
                json_response['message'],
                "User bus direction updated.")

        self.helper.endRoute(travel_key)

    def test_setDirectionWithoutActiveToken(self):
        """ set direction of travel has been finished """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, self.license_plate)
        self.helper.sendFakeTrajectoryOfToken(travel_key)
        self.helper.endRoute(travel_key)

        directions = ["I", "R"]
        for direction in directions:
            json_response = self.helper.setDirection(travel_key, direction)

            self.assertEqual(json_response['valid'], False)
            self.assertEqual(json_response['message'], "Token doesn't exist.")

    def test_setDirectionWithoutActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has been finished """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travel_key)
        self.helper.endRoute(travel_key)

        directions = ["I", "R"]
        for direction in directions:
            json_response = self.helper.setDirection(travel_key, direction)

            self.assertEqual(json_response['valid'], False)
            self.assertEqual(json_response['message'], "Token doesn't exist.")

    def test_setDirectionWithWrongDirection(self):
        """ set direction of travel has been finished """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, self.license_plate)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        directions = ["Z", "S", "other things"]
        for direction in directions:
            json_response = self.helper.setDirection(travel_key, direction)

            self.assertEqual(json_response['valid'], False)
            self.assertEqual(json_response['message'], "Invalid direction.")

        self.helper.endRoute(travel_key)
