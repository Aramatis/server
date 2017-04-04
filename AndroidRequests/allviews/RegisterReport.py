from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.utils import timezone

import logging

import os
# import DB's models
from AndroidRequests.models import Report


class IncorrectExtensionImageError(Exception):
    """ Image extension is not valid """


class EmptyTextMessageError(Exception):
    """ Text message is empty """


class EmptyPhoneIdError(Exception):
    """ PhoneId is empty """


class RegisterReport(View):
    """This class handles requests for report an event not supported by the system."""

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterReport, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ It receives the data for the free report """

        logger = logging.getLogger(__name__)

        fine = False
        message = 'Report saved.'

        if request.method == 'POST':
            text = request.POST.get('text', '')
            stringImage = request.POST.get('img', '')
            if stringImage is not None:
                stringImage = stringImage.decode('base64')
            extension = request.POST.get('ext', '')
            aditionalInfo = request.POST.get('reportInfo', '')
            pPhoneId = request.POST.get('userId', '')
            pTimeStamp = timezone.now()

            try:
                if text == '':
                    raise EmptyTextMessageError
                if pPhoneId == '':
                    raise EmptyPhoneIdError

                report = Report.objects.create(
                    timeStamp=pTimeStamp,
                    phoneId=pPhoneId,
                    message=text,
                    reportInfo=aditionalInfo,
                    imageName=None)
                fine = True
            except EmptyPhoneIdError as e:
                message = 'Has to exist a user id.'
                logger.error(str(e))
            except EmptyTextMessageError as e:
                message = 'Has to exist a text message.'
                logger.error(str(e))
            except (IntegrityError, ValueError) as e:
                message = 'Error to create record.'
                logger.error(str(e))
            else:
                try:
                    if stringImage != '':
                        if extension.upper() not in ['JPG', 'JPEG', 'PNG']:
                            raise IncorrectExtensionImageError

                        imageName = str(
                            report.pk) + "_" + pTimeStamp.strftime('%X_%Y-%m-%d') + "." + extension
                        path = os.path.join(settings.MEDIA_IMAGE, imageName)
                        imageFile = open(path, "wb")
                        imageFile.write(stringImage)
                        imageFile.close()
                        report.imageName = imageName
                        report.save()
                except IncorrectExtensionImageError as e:
                    logger.error(str(e))
                    message = 'Extension image is not valid.'
                    report.delete()
                    fine = False
                except Exception as e:
                    logger.error(str(e))
                    message = 'Error to save image'
                    report.delete()
                    fine = False

        response = {'valid': fine, 'message': message}
        return JsonResponse(response, safe=False)
