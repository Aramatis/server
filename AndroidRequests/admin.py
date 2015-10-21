from django.contrib import admin
from AndroidRequests.models import *


# Register your models here.

admin.site.register(DevicePositionInTime)
admin.site.register(BusStop)
admin.site.register(Bus)
admin.site.register(Event)
admin.site.register(Token)
admin.site.register(PoseInTrajectoryOfToken)
admin.site.register(ActiveToken)