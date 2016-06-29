from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError

import os
# import DB's models
from AndroidRequests.models import *

class IncorrectExtensionImageError(Exception):
    """ Image extension is not valid """

class EmptyTextMessageError(Exception):
    """ Text message is empty """

class EmptyUserIdError(Exception):
    """ UserId is empty """

class RegisterReport(View):
    """This class handles requests for report an event not supported by the system."""
    def __init__(self):
        self.context={}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterReport, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ It receives the data for the free report """
        fine = False
        message = 'Report saved.'

        if request.method == 'POST':
            text = request.POST.get('text', '')
            stringImage = request.POST.get('img', '')
            if stringImage is not None:
                stringImage = stringImage.decode('base64')
            extension = request.POST.get('ext', '')
            aditionalInfo = request.POST.get('report_info', '')
            pUserId = request.POST.get('userId', '')
            pTimeStamp = timezone.now()

            try:
                if text == '':
                    raise EmptyTextMessageError
                if pUserId == '':
                    raise EmptyUserIdError

                report = Report(timeStamp=pTimeStamp, userId=pUserId, \
                                message=text, path="default", reportInfo=aditionalInfo)
                report.save()
                
                if stringImage != '':
                    if extension.upper() not in ['JPG', 'JPEG', 'PNG']:
                        raise IncorrectExtensionImageError

                    path = os.path.join(settings.MEDIA_ROOT, "report_image", str(report.pk) + "." + extension)
                    imageFile = open(path, "wb")
                    imageFile.write(stringImage)
                    imageFile.close()
                    report.path = path
                    report.save()

                fine = True

            except EmptyUserIdError:
                message = 'Has to exist a user id.'
            except EmptyTextMessageError:
                message = 'Has to exist a text message.'
            except (IntegrityError, ValueError):
                message = 'Error to create record.'
            except IncorrectExtensionImageError:
                message = 'Extension image is not valid.'
                report.delete()
            except:
                message = 'Error to save image'
                report.delete()

        response = {'valid': fine, 'message': message}
        return JsonResponse(response, safe=False)

