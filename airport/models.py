import os
import uuid

from django.db import models
from django.utils.text import slugify


class Location(models.Model):
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.city}({self.country})"


def airport_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "airports", filename)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        to=Location,
        on_delete=models.CASCADE,
        related_name="airports"
    )
    image = models.ImageField(
        null=True, upload_to=airport_image_file_path
    )

    def __str__(self) -> str:
        return f"{self.name}({self.location.city})"


class Route(models.Model):
    sourse = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="start_of_route"
    )
    destination = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="end_of_route"
    )

    def __str__(self) -> str:
        return f"{self.sourse} - {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        to=AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Flight(models.Model):
    route = models.ForeignKey(
        to=Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        to=Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField(
        to=Crew, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self) -> str:
        return (f"{self.route.sourse} - {self.route.destination}"
                f"Departure: {str(self.departure_time)}")
