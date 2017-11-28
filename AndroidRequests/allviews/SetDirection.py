from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import ActiveToken, Token
from AndroidRequests.encoder import TranSappJSONEncoder


class SetDirection(View):
    """This class set the direction of user bus. """

    def __init__(self):
        super(SetDirection, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SetDirection, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        response = {}

        if request.method == 'POST':
            token = request.POST.get('pToken', '')
            direction = request.POST.get('pDirection', '')

            if direction in ["I", "R"]:
                if ActiveToken.objects.filter(token__token=token).exists():
                    token_obj = Token.objects.get(token=token)
                    token_obj.direction = direction
                    token_obj.save()

                    response['message'] = 'User bus direction updated.'
                    response['valid'] = True
                else:  # if the token was not found alert
                    response['message'] = 'Token doesn\'t exist.'
                    response['valid'] = False
            else:
                response['message'] = 'Invalid direction.'
                response['valid'] = False

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
