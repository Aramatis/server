from django.http import JsonResponse
from django.views.generic import View

from AndroidRequests.models import ActiveToken, Token
from AndroidRequests.encoder import TranSappJSONEncoder
from AndroidRequests.scoreFunctions import checkCompleteTripScore


class EndRoute(View):
    """This class handles the ending of a trip tracking removing the token
    from the active token table."""

    def __init__(self):
        super(EndRoute, self).__init__()
        self.context = {}

    def post(self, request):
        """Delete the token from the active ones."""
        token = request.POST.get('token')
        purgeType = request.POST.get('purgeType')

        response = {}
        # check if the token exist
        if ActiveToken.objects.filter(token__token=token).exists():
            ActiveToken.objects.get(token__token=token).delete()
            if purgeType in [Token.USER_SAYS_GET_OFF, Token.SERVER_SAYS_GET_OFF,
                             Token.SMARTPHONE_SAYS_IS_FAR_AWAY_FROM_REAL_BUS,
                             Token.SMARTPHONE_SAYS_THAT_THERE_IS_NOT_MOVEMENT]:
                Token.objects.filter(token=token).update(purgeType=purgeType)
            # check if points are valid
            checkCompleteTripScore(token)

            response['response'] = 'Trip ended.'
        else:  # if the token was not found alert
            response['response'] = 'Token doesn\'t exist.'

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get(self, request, pToken):
        """Delete the token from the active ones."""
        response = {}
        # check if the token exist
        if ActiveToken.objects.filter(token__token=pToken).exists():
            ActiveToken.objects.get(token__token=pToken).delete()

            # check if points are valid
            checkCompleteTripScore(pToken)

            response['response'] = 'Trip ended.'
        else:  # if the token was not found alert
            response['response'] = 'Token doesn\'t exist.'

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
