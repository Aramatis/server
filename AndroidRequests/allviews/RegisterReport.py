from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
# import DB's models
from AndroidRequests.models import *

class RegisterReport(View):
	"""This class handles request for the list of bus stop for an specific service."""
	def __init__(self):
		self.context={}

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(RegisterReport, self).dispatch(request, *args, **kwargs)


	def post(self, request):
		"""it receive the data for the free report, receive the ."""
		fine = True
		if request.method == 'POST':
			text = request.POST['text']
			stringImage = request.POST['img'].decode('base64')
			extension = request.POST['ext']
			report = Report(message=text, path="default")
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