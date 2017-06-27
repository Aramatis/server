from django.contrib import admin

from AndroidRequests.models import DevicePositionInTime, Event, EventForBusStop, EventForBusv2, ServicesByBusStop, \
    BusStop, Busv2, ServiceLocation, ServiceStopDistance, Token, PoseInTrajectoryOfToken, ActiveToken

# Register your models here.

admin.site.register(DevicePositionInTime)
admin.site.register(Event)
admin.site.register(EventForBusStop)
admin.site.register(EventForBusv2)
admin.site.register(ServicesByBusStop)
admin.site.register(BusStop)
admin.site.register(Busv2)
admin.site.register(ServiceLocation)
admin.site.register(ServiceStopDistance)
admin.site.register(Token)
admin.site.register(PoseInTrajectoryOfToken)
admin.site.register(ActiveToken)
