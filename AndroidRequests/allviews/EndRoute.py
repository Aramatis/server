from django.http import JsonResponse
from django.views.generic import View

# my stuff
# import DB's models
from AndroidRequests.models import ActiveToken


class EndRoute(View):
    """This class handles the ending of a trip tracking removing the token
    from the active token table."""

    def __init__(self):
        self.context = {}

    def get(self, request, pToken):
        """Delete the token from the active ones."""
        response = {}
        # check if the token exist
        if ActiveToken.objects.filter(token=pToken).exists():
            ActiveToken.objects.get(token=pToken).delete()
            response['response'] = 'Trip ended.'
        else:  # if the token was not found alert
            response['response'] = 'Token doesn\'t exist.'

        return JsonResponse(response, safe=False)
