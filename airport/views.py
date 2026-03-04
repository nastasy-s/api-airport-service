from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
)
from airport.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    RouteSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .select_related(
            "route",
            "airplane",
            "route__source",
            "route__destination",
            "airplane__airplane_type"
        )
        .prefetch_related("crew")
    )
    serializer_class = FlightSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []
        return [IsAdminUser()]


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("tickets")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer
