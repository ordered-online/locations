import math

from django.db import models


class Category(models.Model):
    name = models.TextField(max_length=100, primary_key=True)


class Tag(models.Model):
    name = models.TextField(max_length=100, primary_key=True)


class Location(models.Model):
    # mandatory fields
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    address = models.TextField(max_length=200)

    # optional fields
    user_id = models.IntegerField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    website = models.TextField(max_length=100, null=True, blank=True)
    telephone = models.TextField(max_length=100, null=True, blank=True)

    # many to many fields
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)

    @staticmethod
    def search_bounds(radius, *, latitude, longitude) -> tuple:
        earth_radius = 6378137
        bounds = tuple()
        for r in [radius, -radius]:
            d_lat = r / earth_radius
            d_lon = r / (earth_radius * math.cos(math.pi * latitude / 180))
            lat = latitude + d_lat * 180 / math.pi
            lon = longitude + d_lon * 180 / math.pi
            bounds += (lat, lon)
        return bounds
