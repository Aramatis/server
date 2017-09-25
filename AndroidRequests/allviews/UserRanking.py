from django.db.models import Count
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
        topRanking = []
        ranking = []
        excludedUsers = []

        previousScore = None
        position = 0
        topUsers = TranSappUser.objects. \
                       select_related('level').order_by('-globalScore')[:self.TOP_USERS]
        for topUser in topUsers:
            #excludedUsers.append(topUser.pk)
            if previousScore != topUser.globalScore:
                previousScore = topUser.globalScore
                position += 1
            topUser = topUser.getDictionary()
            topUser['position'] = position
            topRanking.append(topUser)

        positionsUpperUsers = TranSappUser.objects. \
            filter(globalScore__gt=user.globalScore).values('globalScore'). \
            annotate(count=Count('globalScore')).count()
        upperUsers = TranSappUser.objects.select_related('level'). \
                         filter(globalScore__gt=user.globalScore). \
                         order_by('globalScore')[:self.UPPER_USERS]

        position = positionsUpperUsers + 1
        for upperUser in upperUsers:
            if upperUser.pk in excludedUsers:
                continue
            excludedUsers.append(upperUser.pk)
            if previousScore != upperUser.globalScore:
                previousScore = upperUser.globalScore
                position -= 1
            upperUser = upperUser.getDictionary()
            upperUser['position'] = position
            ranking.append(upperUser)

        lowerUsers = TranSappUser.objects. \
                         select_related('level').filter(globalScore__lte=user.globalScore). \
                         order_by('-globalScore')[:self.LOWER_USERS]
        position = positionsUpperUsers
        for lowerUser in lowerUsers:
            if lowerUser.pk in excludedUsers:
                continue
            if previousScore != lowerUser.globalScore:
                previousScore = lowerUser.globalScore
                position += 1
            lowerUser = lowerUser.getDictionary()
            lowerUser['position'] = position
            ranking.append(lowerUser)

        ranking = sorted(ranking, key=lambda el: el['position'])
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
