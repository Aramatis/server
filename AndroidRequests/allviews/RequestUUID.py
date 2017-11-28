from django.http import JsonResponse
from django.views.generic import View

from AndroidRequests.models import Busv2
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.constants as constants
import uuid


class RequestUUID(View):
    """This class get or create an UUID for bus object based on license plate. """

    def get(self, request, license_plate):

        # remove hyphen and convert to uppercase
        license_plate = license_plate.replace("-", "").replace(" ", "").upper()
        response = {}
        if license_plate == constants.DUMMY_LICENSE_PLATE:
            # we will update route when the bus asks for a token
            bus_obj = Busv2.objects.create(registrationPlate=license_plate, uuid=uuid.uuid4())
        else:
            bus_obj = Busv2.objects.get_or_create(registrationPlate=license_plate)[0]

        # we store the active token
        response['uuid'] = bus_obj.uuid

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
