# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import JsonResponse
from django.views import View


class GTFSVersion(View):
    """ return the current version of gtfs in server """

    def get(self, request):
        data = {
            "version": settings.GTFS_VERSION
        }
        return JsonResponse(data, safe=False)
