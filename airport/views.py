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
from rest_framework.decorators import action
from rest_framework.response import Response


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
        if self.action in ("list", "retrieve", "available_seats"):
            return []
        return [IsAdminUser()]

    @action(detail=True, methods=["get"], url_path="available-seats")
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        airplane = flight.airplane

        taken = set(
            flight.ticket_set.values_list("row", "seat")
        )

        available = []
        for row in range(1, airplane.rows + 1):
            for seat in range(1, airplane.seats_in_row + 1):
                if (row, seat) not in taken:
                    available.append({"row": row, "seat": seat})

        total = airplane.rows * airplane.seats_in_row

        return Response({
            "flight_id": flight.id,
            "total_seats": total,
            "taken_seats": len(taken),
            "available_seats": len(available),
            "results": available,
        })


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
