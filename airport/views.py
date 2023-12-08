from datetime import datetime

from django.db.models import F, Count
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Location,
    Route,
    Flight
)

from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    LocationSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportImageSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer


class LocationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        if self.action == "upload_image":
            return AirportImageSerializer

        return AirportSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        # permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airport"""
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer

    def get_queryset(self):
        depart_date = self.request.query_params.get("depart_date")
        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")

        queryset = self.queryset

        if depart_date:
            date = datetime.strptime(
                depart_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                departure_time__date=date
            )

        if departure:
            queryset = queryset.filter(
                route__source__name__icontains=departure
            )

        if arrival:
            queryset = queryset.filter(
                route__destination__name__icontains=arrival
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer
