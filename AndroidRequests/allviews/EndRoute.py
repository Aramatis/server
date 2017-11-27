from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from AndroidRequests.models import ActiveToken, Token
from AndroidRequests.encoder import TranSappJSONEncoder
from AndroidRequests.scoreFunctions import checkCompleteTripScore
from AndroidRequests.statusResponse import Status


class EndRoute(View):
    """This class handles the ending of a trip tracking removing the token
    from the active token table."""

    def __init__(self):
        super(EndRoute, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(EndRoute, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """Delete the token from the active ones."""
        token = request.POST.get('token')
        purge_cause = request.POST.get('purgeCause')

        response = {}
        # check if the token exist
        if ActiveToken.objects.filter(token__token=token).exists():
            ActiveToken.objects.get(token__token=token).delete()
            if purge_cause in [Token.USER_SAYS_GET_OFF, Token.SERVER_SAYS_GET_OFF,
                               Token.SMARTPHONE_SAYS_IS_FAR_AWAY_FROM_REAL_BUS,
                               Token.SMARTPHONE_SAYS_THAT_THERE_IS_NOT_MOVEMENT]:
                Token.objects.filter(token=token).update(purgeCause=purge_cause)
            # check if points are valid
            checkCompleteTripScore(token)

            Status.getJsonStatus(Status.OK, response)
        else:  # if the token was not found alert
            Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get(self, request, token):
        """Delete the token from the active ones."""
        response = {}
        # check if the token exist
        if ActiveToken.objects.filter(token__token=token).exists():
            ActiveToken.objects.get(token__token=token).delete()

            # check if points are valid
            checkCompleteTripScore(token)

            response['response'] = 'Trip ended.'
        else:  # if the token was not found alert
            response['response'] = 'Token doesn\'t exist.'

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
