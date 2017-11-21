# encoding=utf-8
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import Token
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder
from AndroidRequests import scoreFunctions as score


class EvaluateTrip(View):
    """ view to evaluate trip of user """

    def __init__(self):
        super(EvaluateTrip, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(EvaluateTrip, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ evaluate trip """

        token = request.POST.get('token', '') 
        evaluation = request.POST.get('evaluation', '') 
        
        response = {}
        try:
            if Token.objects.filter(token=token).exists():
                token = Token.objects.get(token=token)
                token.userEvaluation = int(evaluation)
                token.save()
                # add score
                event_id = "evn00301"
                meta = {"token": token.token}
                response.update(score.calculateEventScore(request, event_id, meta))
                Status.getJsonStatus(Status.OK, response)
            else:
                Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)
        except ValueError:
            Status.getJsonStatus(Status.TRIP_EVALUATION_FORMAT_ERROR, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

