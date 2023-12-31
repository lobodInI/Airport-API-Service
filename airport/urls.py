from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    LocationViewSet,
    AirportViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("locations", LocationViewSet)
router.register("airports", AirportViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)

urlpatterns = router.urls

app_name = "airport"
