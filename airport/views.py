from datetime import datetime
from typing import Type

from django.db.models import F, Count, QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Location,
    Route,
    Flight,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly

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
    FlightDetailSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> Type[Serializer]:
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return AirportListSerializer

        if self.action == "upload_image":
            return AirportImageSerializer

        return AirportSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None) -> Response:
        """Endpoint for uploading image to specific airport"""
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> Type[Serializer]:
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet:
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

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="depart_date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by datetime of flights "
                    "(ex. ?date=2023-12-23)"),
            ),
            OpenApiParameter(
                name="departure",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by name airport of flights "
                    "(ex. ?departure=heathrow)"
                ),
            ),
            OpenApiParameter(
                name="arrival",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by name airport of flights "
                    "(ex. ?arrival=boryspil)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs) -> list:
        return super().list(request, *args, **kwargs)
