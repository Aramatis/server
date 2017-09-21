from django.http import JsonResponse
from django.views.generic import View

from AndroidRequests.models import Busv2
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.constants as Constants
import uuid


class RequestUUID(View):
    """This class get or create an UUID for bus object based on license plate. """

    def __init__(self):
        self.context = {}

    def get(self, request, pLicensePlate):

        # remove hyphen and convert to uppercase
        pLicensePlate = pLicensePlate.replace('-', '').upper()
        response = {}
        if pLicensePlate == Constants.DUMMY_LICENSE_PLATE:

            puuid = uuid.uuid4()

            # we will update service when the bus asks for a token
            busv2 = Busv2.objects.create(registrationPlate=pLicensePlate,
                                         uuid=puuid)
        else:
            busv2 = Busv2.objects.get_or_create(
                registrationPlate=pLicensePlate)[0]

        # we store the active token
        response['uuid'] = busv2.uuid

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
