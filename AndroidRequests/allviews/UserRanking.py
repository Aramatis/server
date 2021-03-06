from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction

from collections import defaultdict

from AndroidRequests.models import TranSappUser
from AndroidRequests.scoreFunctions import UserValidation
from AndroidRequests.encoder import TranSappJSONEncoder


class UserRanking(View):
    """ global user ranking """
    TOP_USERS = 5
    UPPER_USERS = 5
    LOWER_USERS = 5

    def getRanking(self, user):
        """ return ranking list """

        with transaction.atomic():
            topUsers = TranSappUser.objects.select_related("level"). \
                            order_by("-globalScore", "globalPosition")[:self.TOP_USERS]
            upperUsers = TranSappUser.objects.select_related("level").filter(globalScore__gt=user.globalScore). \
                             order_by("globalScore", "globalPosition")[:self.UPPER_USERS]
            lowerUsers = TranSappUser.objects.select_related("level").filter(globalScore__lte=user.globalScore). \
                             order_by("-globalScore", "globalPosition")[:self.LOWER_USERS]

        topRanking = [topUser.getDictionary() for topUser in topUsers]
        nearRanking = [upperUser.getDictionary() for upperUser in upperUsers]
        nearRanking.reverse()
        nearRanking += [lowerUser.getDictionary() for lowerUser in lowerUsers]

        # if user ask between updates simulate position
        cache = {}
        newTopRanking = []
        position = 0
        for user in topRanking:
            if user["globalScore"] in user.keys():
                user["ranking"]["globalPosition"] = cache[user["globalScore"]]
            else:
                position += 1
                cache[user["globalScore"]] = position
                user["ranking"]["globalPosition"] = position
            newTopRanking.append(user)

        newNearRanking = []
        position = nearRanking[0]["ranking"]["globalPosition"] - 1 if len(nearRanking) > 0 else None
        for user in nearRanking:
            if user["globalScore"] in user.keys():
                user["ranking"]["globalPosition"] = cache[user["globalScore"]]
            else:
                position += 1
                cache[user["globalScore"]] = position
                user["ranking"]["globalPosition"] = position
            newNearRanking.append(user)

        return newTopRanking, newNearRanking

    def get(self, request):
        """return list of ranking with @TOP_USERS + @UPPER_USERS + @LOWER_USERS """

        userId = request.GET.get("userId")
        sessionToken = request.GET.get("sessionToken")

        loggedUser, user, statusResponse = UserValidation().validateUser(userId, sessionToken)

        response = defaultdict(dict)
        response.update(statusResponse)

        if loggedUser:
            response["ranking"]["top"], response["ranking"]["near"] = self.getRanking(user)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
