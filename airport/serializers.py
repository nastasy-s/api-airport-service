from __future__ import annotations

from django.db import IntegrityError, transaction
from rest_framework import serializers

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
    Ticket,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    source_id = serializers.PrimaryKeyRelatedField(
        source="source",
        queryset=Airport.objects.all(),
        write_only=True,
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Airport.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "source_id",
            "destination_id",
            "distance"
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        source="airplane_type",
        queryset=AirplaneType.objects.all(),
        write_only=True,
    )
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "airplane_type_id",
            "capacity",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    route_id = serializers.PrimaryKeyRelatedField(
        source="route",
        queryset=Route.objects.all(),
        write_only=True,
    )
    airplane_id = serializers.PrimaryKeyRelatedField(
        source="airplane",
        queryset=Airplane.objects.all(),
        write_only=True,
    )
    crew_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source="crew",
        queryset=Crew.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "route_id",
            "airplane",
            "airplane_id",
            "crew",
            "crew_ids",
            "departure_time",
            "arrival_time",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "flight", "row", "seat")

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]

        airplane = flight.airplane

        if row > airplane.rows:
            raise serializers.ValidationError(
                {"row": "Row number exceeds airplane capacity"}
            )

        if seat > airplane.seats_in_row:
            raise serializers.ValidationError(
                {"seat": "Seat number exceeds seats per row"}
            )

        return attrs


class TicketCreateSerializer(serializers.ModelSerializer):
    flight_id = serializers.PrimaryKeyRelatedField(
        source="flight",
        queryset=Flight.objects.all(),
    )

    class Meta:
        model = Ticket
        fields = ("flight_id", "row", "seat")

    def validate(self, attrs):
        flight = attrs["flight"]
        row = attrs["row"]
        seat = attrs["seat"]

        airplane = flight.airplane

        if row < 1:
            raise serializers.ValidationError({"row": "Row must be >= 1"})
        if seat < 1:
            raise serializers.ValidationError({"seat": "Seat must be >= 1"})

        if row > airplane.rows:
            raise serializers.ValidationError(
                {"row": f"Row must be between 1 and {airplane.rows} for this airplane"}
            )

        if seat > airplane.seats_in_row:
            raise serializers.ValidationError(
                {"seat": f"Seat must be between 1 and {airplane.seats_in_row} for this airplane"}
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "tickets")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets", [])
        user = self.context["request"].user

        seen: set[tuple[int, int, int]] = set()
        for t in tickets_data:
            flight_id = t["flight"].id
            key = (flight_id, t["row"], t["seat"])
            if key in seen:
                raise serializers.ValidationError(
                    {"tickets": "Duplicate seat found in request payload."}
                )
            seen.add(key)

        order = Order.objects.create(user=user)

        for ticket_data in tickets_data:
            ticket = Ticket(order=order, **ticket_data)

            ticket.full_clean()

            try:
                ticket.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    {"tickets": "One or more seats are already taken for this flight."}
                )

        return order
