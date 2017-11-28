from datetime import datetime

from django.test import TransactionTestCase
from django.http import JsonResponse

from AndroidRequests.encoder import TranSappJSONEncoder

import uuid


class EncoderTest(TransactionTestCase):

    def test_DictWithUUIDField(self):
        """ serialize dictionary with uuid attribute """

        # create object
        datetime_object = datetime.now()

        test_dict = {
            "uuid": uuid.uuid4(),
            "text": "hello",
            "integer": 0,
            "boolean": True,
            "obj": datetime_object
        }

        JsonResponse(test_dict, encoder=TranSappJSONEncoder)
