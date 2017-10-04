from django.http import JsonResponse
from django.views.generic import View

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
        topUsers = TranSappUser.objects.select_related('level'). \
                        order_by("globalPosition", "-globalScore")[:self.TOP_USERS]
        topRanking = [topUser.getDictionary(with_ranking=True) for topUser in topUsers]

        upperUsers = TranSappUser.objects.select_related('level').filter(globalScore__gt=user.globalScore). \
                         order_by("-globalPosition", "globalScore")[:self.UPPER_USERS]
        ranking = [upperUser.getDictionary(with_ranking=True) for upperUser in upperUsers]
        ranking.reverse()

        lowerUsers = TranSappUser.objects.select_related('level').filter(globalScore__lte=user.globalScore). \
                         order_by("globalPosition", '-globalScore')[:self.LOWER_USERS]
        ranking += [lowerUser.getDictionary(with_ranking=True) for lowerUser in lowerUsers]

        return topRanking, ranking

    def get(self, request):
        """return list of ranking with @TOP_USERS + @UPPER_USERS + @LOWER_USERS """

        userId = request.GET.get('userId')
        sessionToken = request.GET.get('sessionToken')

        loggedUser, user, statusResponse = UserValidation().validateUser(userId, sessionToken)

        response = defaultdict(dict)
        response.update(statusResponse)

        if loggedUser:
            response['ranking']['top'], response['ranking']['near'] = self.getRanking(user)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
