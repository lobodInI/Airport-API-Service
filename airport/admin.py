from django.contrib import admin

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Location,
    Route,
    Flight,
)

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Crew)
admin.site.register(Location)
admin.site.register(Route)
admin.site.register(Flight)
