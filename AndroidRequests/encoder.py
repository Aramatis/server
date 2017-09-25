from django.core.serializers.json import DjangoJSONEncoder
from uuid import UUID

class TranSappJSONEncoder(DjangoJSONEncoder):
    """ serializer to process uuid objects """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super(TranSappJSONEncoder, self).default(obj)
