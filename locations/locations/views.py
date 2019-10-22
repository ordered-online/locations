import json
from decimal import Decimal

from django.core import serializers
from django.forms import model_to_dict
from django.http import JsonResponse

from locations import settings
from locations.models import Location, Tag, Category


def find_locations(request):
    if request.method != "GET":
        return JsonResponse({"success": False})

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

    return JsonResponse(
        json.loads(serializers.serialize("json", locations)),
        safe=False
    )


def find_nearby_locations(request):
    if request.method != "GET":
        return JsonResponse({"success": False})

    locations = Location.objects.all()

    try:
        longitude = float(request.GET.get("longitude"))
        latitude = float(request.GET.get("latitude"))
    except (ValueError, TypeError):
        return JsonResponse({"success": False})

    radius = float(request.GET.get("radius", settings.DEFAULT_SEARCH_RADIUS))
    max_lat, max_lon, min_lat, min_lon = Location.search_bounds(
        radius, latitude=latitude, longitude=longitude
    )

    locations = locations.filter(
        latitude__gte=Decimal(min_lat),
        latitude__lte=Decimal(max_lat),
        longitude__gte=Decimal(min_lon),
        longitude__lte=Decimal(max_lon),
    )

    return JsonResponse(
        json.loads(serializers.serialize("json", locations)),
        safe=False
    )


def get_location(request, location_id):
    if request.method != "GET":
        return JsonResponse({"success": False})

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return JsonResponse({"success": False})

    location_dict = model_to_dict(location)

    categories = location_dict.get("categories")
    if categories:
        location_dict["categories"] = [model_to_dict(c) for c in categories]

    categories = location_dict.get("tags")
    if categories:
        location_dict["tags"] = [model_to_dict(c) for c in categories]

    return JsonResponse(location_dict)

