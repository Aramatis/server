# encoding=utf-8
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# python utilities
import logging
import requests
import uuid
import re
import json

from AndroidRequests.models import Token

# Create your views here.

class EvaluateTrip(View):
    ''' log in transapp user '''

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(EvaluateTrip, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ evaluate trip """

        token = request.POST.get('token', '') 
        evaluation = request.POST.get('evaluation', '') 
        
        response = {}
        response['status'] = 403
        response['message'] = 'Trip token does not exist'
        try:
            if Token.objects.filter(token=token).update(userEvaluation=int(evaluation)):
                response['status'] = 200
                response['message'] = 'ok'
        except:
            response['status'] = 404
            response['message'] = 'Evaluation format is wrong'

        return JsonResponse(response, safe=False)

