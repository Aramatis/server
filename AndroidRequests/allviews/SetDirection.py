from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

#python utilities
import json

# my stuff
# import DB's models
from AndroidRequests.models import ActiveToken, Token 

class SetDirection(View):
    """This class set the direction of user bus. """
    def __init__(self):
        self.context={}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SetDirection, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        response = {}

        if request.method == 'POST':
            pToken = request.POST.get('pToken', '')
            pDirection = request.POST.get('pDirection', '')

            if ActiveToken.objects.filter(token=pToken).exists():
                aToken = Token.objects.get(token=pToken)
                aToken.direction = pDirection
                aToken.save()

                response['message'] = 'User bus direction updated.'
                response['valid'] = True
            else:#if the token was not found alert
                response['message'] = 'Token doesn\'t exist.'
                response['valid'] = False

        return JsonResponse(response, safe=False)
