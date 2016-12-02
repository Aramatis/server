# encoding=utf-8
from django.test import TestCase, RequestFactory
# views
import routeplanner.views as views
from routeplanner.views import RoutePlanner


class RoutePlannerTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        self.factory = RequestFactory()
        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

    def test_getCitySuffix(self):
        """   """

        origin = "-33.456769,-70.652883"
        destination = "beauchef 850"

        view = RoutePlanner()

        newOrigin = view.addCitySuffix(origin)
        newDestination = view.addCitySuffix(destination)

        self.assertEqual(origin, newOrigin)
        self.assertEqual(destination + " " + views.CITY_SUFFIX, newDestination)

    def test_getCitySuffixWithAccentWord(self):
        """   """

        origin = "-33.456769,-70.652883"
        destination = "Universidad del pacífico"

        view = RoutePlanner()

        newOrigin = view.addCitySuffix(origin)
        newDestination = view.addCitySuffix(destination)

        self.assertEqual(origin, newOrigin)
        self.assertEqual(destination + " " + views.CITY_SUFFIX, newDestination)


"""
        jsonResponse = self.calculateTrip(self.userIf, pOrigin, pDestination)

        self.assertEqual(len(jsonResponse), 4)

    def calculateTrip(self, userId, origin, destination):
        URL = '/routeplanner/calculate'
        request = self.factory.get(URL)
        request.user = AnonymousUser()
        reponseView = RoutePlanner()
        response = reponseView.get(request, origin, destination)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
"""
