from rest_framework import serializers
from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket

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
          write_only=True
      )
      destination_id = serializers.PrimaryKeyRelatedField(
          source="destination",
          queryset=Airport.objects.all(),
          write_only=True
      )

      class Meta:
          model = Route
          fields = ("id", "source","destination", "destination_id", "source_id", "distance")

class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")

class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        source="airplane_type",
        queryset=AirplaneType.objects.all(),
        write_only=True
    )
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type","airplane_type_id", "capacity") #  noqa501

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id","first_name", "last_name")

class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        source="route",
        queryset=Route.objects.all(),
        write_only=True
    )
    airplane_id = serializers.PrimaryKeyRelatedField(
        source="airplane",
        queryset=Airplane.objects.all(),
        write_only=True
    )
    crew_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source="crew",
        queryset=Crew.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Flight
        fields = ("id",
                  "route",
                  "airplane",
                  "crew","route_id",
                  "airplane_id",
                  "crew_ids",
                  "departure_time",
                  "arrival_time"
                  )
