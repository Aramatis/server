from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
# import DB's models
from AndroidRequests.models import *

class RegisterReport(View):
	"""This class handles requests for report an event not supported by the system."""
	def __init__(self):
		self.context={}

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(RegisterReport, self).dispatch(request, *args, **kwargs)


	def post(self, request):
		"""It receives the data for the free report, receives a text, 
		an image and the extension for that image."""
		fine = True
		if request.method == 'POST':
			text = request.POST['text']
			stringImage = request.POST['img'].decode('base64')
			extension = request.POST['ext']
			aditionalInfo = request.POST['report_info']

			report = Report(message=text, path="default", reportInfo=aditionalInfo)
			report.save()
			
			try:
				path = os.path.join(settings.MEDIA_ROOT, "report_image", str(report.pk) + "." + extension)
				imageFile = open(path, "wb")
				imageFile.write(stringImage)
				imageFile.close()
				report.path = path
				report.save()
			except:
				report.delete()
				fine = False
		else:
			fine = False
		response = {'valid': fine}
		return JsonResponse(response, safe=False)