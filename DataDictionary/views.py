from django.shortcuts import render
from django.views.generic import View

# Create your views here.

class ShowDocModel(View):
	"""This class displays the data dictionary of the model.
	To update the document see parseMKtoHTML in the templates folder."""	

	def __init__(self):
		"""The contructor, context are the parameter given to the html template."""
		self.context={}	

	def get(self, request):

		template = "dataDic.html"

		return render(request, template, self.context)