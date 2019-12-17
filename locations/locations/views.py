import json
from decimal import Decimal
from json import JSONDecodeError

import requests
from django.db import IntegrityError
from django.http import JsonResponse

from . import settings
from .models import Location, Tag, Category


class SuccessResponse(JsonResponse):
    status_code = 200

    def __init__(self, response=None, *args, **kwargs):
        if response is None:
            super().__init__({}, *args, **kwargs)
        else:
            super().__init__(response, *args, **kwargs)


class AbstractFailureResponse(JsonResponse):
    reason = None

    def __init__(self, *args, **kwargs):
        super().__init__({"reason": self.reason}, *args, **kwargs)


class IncorrectAccessMethod(AbstractFailureResponse):
    reason = "incorrect_access_method"
    status_code = 405


class ErroneousValue(AbstractFailureResponse):
    reason = "erroneous_value"
    status_code = 400


class LocationNotFound(AbstractFailureResponse):
    reason = "location_not_found"
    status_code = 404


class IncorrectSessionKey(AbstractFailureResponse):
    reason = "incorrect_session_key"
    status_code = 403


class IncorrectUserId(AbstractFailureResponse):
    reason = "incorrect_user_id"
    status_code = 403


class MalformedJson(AbstractFailureResponse):
    reason = "malformed_json"
    status_code = 400


class IncorrectCredentials(AbstractFailureResponse):
    reason = "incorrect_credentials"
    status_code = 403


class DuplicateLocation(AbstractFailureResponse):
    reason = "duplicate_location"
    status_code = 400


class VerificationServiceUnavailable(AbstractFailureResponse):
    reason = "verification_service_unavailable"
    status_code = 503


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
            location.dict_representation
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
        # the radius query parameter is optional
        radius = float(request.GET.get("radius", settings.DEFAULT_SEARCH_RADIUS))
    except (ValueError, TypeError):
        return ErroneousValue()

    # compute the search bounds as longitudinal and latitudinal values
    max_lat, max_lon, min_lat, min_lon = Location.search_bounds(
        radius, latitude=latitude, longitude=longitude
    )

    # search the location by django orm
    locations = locations.filter(
        latitude__gte=Decimal(min_lat),
        latitude__lte=Decimal(max_lat),
        longitude__gte=Decimal(min_lon),
        longitude__lte=Decimal(max_lon),
    )

    # limit the results by a certain amount
    locations = locations[:settings.MAX_RESULTS]

    return SuccessResponse(
        [
            {
                "distance": location.distance_from(longitude=longitude, latitude=latitude),
                "location": location.dict_representation
            }
            for location in locations
        ],
        # disable safe mode, because otherwise, the list could not be serialized
        # and we are sure, that all data is safe
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

    # send a post request to the verification service endpoint
    response = requests.post(
        "{}/verification/verify/".format(settings.VERIFICATION_SERVICE_URL),
        data=json.dumps({"session_key": session_key, "user_id": user_id})
    )

    if response.status_code is not 200:
        raise ValueError()

    return user_id, session_key


def make_location(location_data: dict) -> JsonResponse:
    """Translate the given location data to a location model."""

    # infer all kwargs from the passed location data,
    # but exclude the many to many fields,
    # since they must be handled separately
    location = Location(**{
        x: location_data[x] for x in location_data
        if x not in ["tags", "categories"]
    })
    try:
        # do not use objects.create to allow id based location editing
        location.save()
    except IntegrityError:
        # if the passed location data violates any
        # uniqueness constraints, this fallback is called
        return DuplicateLocation()

    tags = location_data.get("tags")
    if tags:
        # infer all kwargs from the passed location data
        location.tags.set(Tag.objects.get_or_create(**t)[0] for t in tags)

    categories = location_data.get("categories")
    if categories:
        # infer all kwargs from the passed location data
        location.categories.set(Category.objects.get_or_create(**c)[0] for c in categories)

    return SuccessResponse(location.dict_representation)


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

    # this is necessary, because the user
    # should not create locations with another
    # user id than his own
    location_data["user_id"] = user_id

    # the key "id" is disallowed, because django
    # would interpret the id key as the primary key
    # of the location object and therefore change
    # the properties of a potentially existing location
    if "id" in location_data:
        return MalformedJson()

    return make_location(location_data)


def edit_location(request, location_id) -> JsonResponse:
    """Edit the given location via POST."""

    if request.method != "POST":
        return IncorrectAccessMethod()

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return LocationNotFound()

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

    # ensure, that the fetched location
    # belongs to the user
    if user_id != location.user_id:
        return IncorrectCredentials()

    location_data = data.get("location")
    if not location_data:
        return MalformedJson()

    # disallow the key "id" to avoid overriding of
    # the wrong location, because the id of the location is
    # already inferred by the url
    if "id" in location_data:
        return MalformedJson()

    # avoid overriding of the wrong location
    # due to erroneous user ids being passed
    location_data["user_id"] = user_id

    # set the id attribute as inferred by the url
    # to make it possible for django to edit
    # the correct object
    location_data["id"] = location.id

    return make_location(location_data)


