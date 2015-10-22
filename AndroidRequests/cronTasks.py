from AndroidRequests.models import ActiveToken
from django.utils import timezone

def cleanActiveTokenTable():
	"""To clean the active tokens table on the DB. This chechs that the last time a 
	token was granted with new position doen't exeede a big amount of time."""

	activeTokens = ActiveToken.objects.all()
	currentTimeMinus11Minutes = timezone.now() - timezone.timedelta(minutes=30)
	for aToken in activeTokens:
		if aToken.timeStamp < currentTimeMinus11Minutes:
			aToken.delete()