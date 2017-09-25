from django.test import TransactionTestCase
from django.http import JsonResponse

from AndroidRequests.encoder import TranSappJSONEncoder

from datetime import datetime

import uuid


class EncoderTest(TransactionTestCase):

    def setUp(self):
        pass

    def test_DictWithUUIDField(self):
        """ serialize dictionary with uuid attribute  """

        # create object
        object = datetime.now()

        test_dict = {
            "uuid": uuid.uuid4(),
            "text": "hello",
            "integer": 0,
            "boolean": True,
            "obj": object
        }

        JsonResponse(test_dict, encoder=TranSappJSONEncoder)
