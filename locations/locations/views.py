import json
from decimal import Decimal
from json import JSONDecodeError

import requests
from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View

from . import settings
from .models import Location, Tag, Category


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


class IncorrectSessionKey(AbstractFailureResponse):
    reason = "incorrect_session_key"


class IncorrectUserId(AbstractFailureResponse):
    reason = "incorrect_user_id"


class MalformedJson(AbstractFailureResponse):
    reason = "malformed_json"


class IncorrectCredentials(AbstractFailureResponse):
    reason = "incorrect_credentials"


class DuplicateLocation(AbstractFailureResponse):
    reason = "duplicate_location"


class VerificationServiceUnavailable(AbstractFailureResponse):
    reason = "verification_service_unavailable"


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


def verify_user(data: dict) -> tuple:
    """Verify the user with the verification service."""
    session_key = data.get("session_key")
    if not session_key:
        raise ValueError()
    user_id = data.get("user_id")
    if not user_id:
        raise ValueError()

    response = requests.post(
        "{}/verification/verify/".format(settings.VERIFICATION_SERVICE_URL),
        data=json.dumps({"session_key": session_key, "user_id": user_id})
    )
    verification_data = response.json()
    if verification_data.get("success") is not True:
        raise ValueError()

    return user_id, session_key


def create_location(request) -> JsonResponse:
    """Create a location via POST."""
    if request.method != "POST":
        return IncorrectAccessMethod()

    try:
        data = json.loads(request.body)
    except JSONDecodeError:
        return MalformedJson()

    try:
        user_id, session_key = verify_user(data)
    except ValueError:
        return IncorrectCredentials()
    except requests.ConnectionError:
        return VerificationServiceUnavailable()

    location_data = data.get("location")
    if not location_data:
        return MalformedJson()

    if "id" in location_data:
        return MalformedJson()

    location = Location(**{
        x: location_data[x] for x in location_data
        if x not in ["tags", "categories"]
    })
    if location.user_id != user_id:
        return MalformedJson()
    try:
        location.save()
    except IntegrityError:
        return DuplicateLocation()

    tags = location_data.get("tags")
    if tags:
        for tag in tags:
            tag, _ = Tag.objects.get_or_create(**tag)
            location.tags.add(tag)

    categories = location_data.get("categories")
    if categories:
        for category in categories:
            category, _ = Category.objects.get_or_create(**category)
            location.categories.add(category)

    return SuccessResponse()


