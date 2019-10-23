import json
from decimal import Decimal

from django.core import serializers
from django.http import JsonResponse

from locations import settings
from locations.models import Location, Tag, Category


class SuccessResponse(JsonResponse):
    def __init__(self, response=None, *args, **kwargs):
        if response is None:
            super().__init__({
                "success": True,
            }, *args, **kwargs)
        else:
            super().__init__({
                "success": True,
                "response": response
            }, *args, **kwargs)


class AbstractFailureResponse(JsonResponse):
    reason = None

    def __init__(self, *args, **kwargs):
        super().__init__({
            "success": False,
            "reason": self.reason
        }, *args, **kwargs)


class IncorrectAccessMethod(AbstractFailureResponse):
    reason = "incorrect_access_method"


class ErroneousValue(AbstractFailureResponse):
    reason = "erroneous_value"


class LocationNotFound(AbstractFailureResponse):
    reason = "location_not_found"


def find_locations(request) -> JsonResponse:
    """Find locations via GET."""

    if request.method != "GET":
        return IncorrectAccessMethod()

    locations = Location.objects.all()

    user_id = request.GET.get("user_id")
    if user_id:
        locations = locations.filter(user_id__exact=user_id)

    name = request.GET.get("name")
    if name:
        locations = locations.filter(name__icontains=name)

    category = request.GET.get("category")
    if category:
        try:
            category = Category.objects.get(name__iexact=category)
        except Category.DoesNotExist:
            pass
        else:
            locations = locations.intersection(category.location_set.all())

    tag = request.GET.get("tag")
    if tag:
        try:
            tag = Tag.objects.get(name__iexact=tag)
        except Tag.DoesNotExist:
            pass
        else:
            locations = locations.intersection(tag.location_set.all())

    locations = locations[:settings.MAX_RESULTS]

    return SuccessResponse(
        [
            {
                "location": location.dict_representation
            }
            for location in locations
        ],
        safe=False
    )


def find_nearby_locations(request) -> JsonResponse:
    """Find locations near a given coordinate via GET."""

    if request.method != "GET":
        return IncorrectAccessMethod()

    locations = Location.objects.all()

    try:
        longitude = float(request.GET.get("longitude"))
        latitude = float(request.GET.get("latitude"))
        radius = float(request.GET.get("radius", settings.DEFAULT_SEARCH_RADIUS))
    except (ValueError, TypeError):
        return ErroneousValue()

    max_lat, max_lon, min_lat, min_lon = Location.search_bounds(
        radius, latitude=latitude, longitude=longitude
    )

    locations = locations.filter(
        latitude__gte=Decimal(min_lat),
        latitude__lte=Decimal(max_lat),
        longitude__gte=Decimal(min_lon),
        longitude__lte=Decimal(max_lon),
    )

    locations = locations[:settings.MAX_RESULTS]

    return SuccessResponse(
        [
            {
                "distance": location.distance_from(longitude=longitude, latitude=latitude),
                "location": location.dict_representation
            }
            for location in locations
        ],
        safe=False
    )


def get_location(request, location_id) -> JsonResponse:
    """Get a location by its id via GET."""

    if request.method != "GET":
        return IncorrectAccessMethod()

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return LocationNotFound()

    return SuccessResponse(location.dict_representation)

