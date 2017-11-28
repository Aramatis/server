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

    def get_ranking(self, user):
        """ return ranking list """

        with transaction.atomic():
            top_users = TranSappUser.objects.select_related("level"). \
                            order_by("-globalScore", "globalPosition")[:self.TOP_USERS]
            upper_users = TranSappUser.objects.select_related("level").filter(globalScore__gt=user.globalScore). \
                              order_by("globalScore", "globalPosition")[:self.UPPER_USERS]
            lower_users = TranSappUser.objects.select_related("level").filter(globalScore__lte=user.globalScore). \
                              order_by("-globalScore", "globalPosition")[:self.LOWER_USERS]

        top_ranking = [top_user.get_dictionary() for top_user in top_users]
        near_ranking = [upper_user.get_dictionary() for upper_user in upper_users]
        near_ranking.reverse()
        near_ranking += [lower_user.get_dictionary() for lower_user in lower_users]

        # if user ask between updates simulate position
        cache = {}
        new_top_ranking = []
        position = 0
        for user in top_ranking:
            if user["globalScore"] in user.keys():
                user["ranking"]["globalPosition"] = cache[user["globalScore"]]
            else:
                position += 1
                cache[user["globalScore"]] = position
                user["ranking"]["globalPosition"] = position
            new_top_ranking.append(user)

        new_near_ranking = []
        position = near_ranking[0]["ranking"]["globalPosition"] - 1 if len(near_ranking) > 0 else None
        for user in near_ranking:
            if user["globalScore"] in user.keys():
                user["ranking"]["globalPosition"] = cache[user["globalScore"]]
            else:
                position += 1
                cache[user["globalScore"]] = position
                user["ranking"]["globalPosition"] = position
            new_near_ranking.append(user)

        return new_top_ranking, new_near_ranking

    def get(self, request):
        """return list of ranking with @TOP_USERS + @UPPER_USERS + @LOWER_USERS """

        user_id = request.GET.get("userId")
        session_token = request.GET.get("sessionToken")

        logged_user, user, status_response = UserValidation().validate_user(user_id, session_token)

        response = defaultdict(dict)
        response.update(status_response)

        if logged_user:
            response["ranking"]["top"], response["ranking"]["near"] = self.get_ranking(user)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
