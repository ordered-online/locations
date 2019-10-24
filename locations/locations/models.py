import math

from django.db import models
from django.forms import model_to_dict


class Category(models.Model):
    name = models.TextField(max_length=100, primary_key=True)


class Tag(models.Model):
    name = models.TextField(max_length=100, primary_key=True)


class Location(models.Model):
    # mandatory fields
    name = models.TextField(unique=True, max_length=100)
    description = models.TextField(max_length=500)
    address = models.TextField(unique=True, max_length=200)
    user_id = models.IntegerField()

    # optional fields
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    website = models.TextField(max_length=100, null=True, blank=True)
    telephone = models.TextField(max_length=100, null=True, blank=True)

    # many to many fields
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    class Meta:
        unique_together = ["latitude", "longitude"]

    @property
    def dict_representation(self):
        location_dict = model_to_dict(self)

        # Serialize many to many fields manually
        categories = location_dict.get("categories")
        if categories:
            location_dict["categories"] = [model_to_dict(c) for c in categories]
        tags = location_dict.get("tags")
        if tags:
            location_dict["tags"] = [model_to_dict(c) for c in tags]

        return location_dict

    def distance_from(self, *, latitude, longitude):
        """
        Compute the distance of the location to a given
        set of coordinates in meters.
        """
        earth_radius = 6378137

        lat_1 = math.radians(self.latitude)
        lon_1 = math.radians(self.longitude)
        lat_2 = math.radians(latitude)
        lon_2 = math.radians(longitude)

        d_lon = lon_2 - lon_1
        d_lat = lat_2 - lat_1

        a = math.sin(d_lat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c

    @staticmethod
    def search_bounds(radius, *, latitude, longitude) -> tuple:
        """
        Compute the search bounds in degrees around a given location.

        The search bounds represent a rectangle of the following manner:
        (max_lat, max_lon, min_lat, min_lon)

        As a tuple, these bounds can be used to efficiently
        fetch locations within a radius of a given location,
        e.g. directly through django ORM.
        """
        earth_radius = 6378137
        bounds = tuple()
        for r in [radius, -radius]:
            d_lat = r / earth_radius
            d_lon = r / (earth_radius * math.cos(math.pi * latitude / 180))
            lat = latitude + d_lat * 180 / math.pi
            lon = longitude + d_lon * 180 / math.pi
            bounds += (lat, lon)
        return bounds
