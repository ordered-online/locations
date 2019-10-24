from django.core.management import BaseCommand
from decimal import Decimal

from locations.models import Category, Location, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        cafe = Category.objects.create(name="Cafe")
        restaurant = Category.objects.create(name="Restaurant")
        bar = Category.objects.create(name="Bar")

        calm = Tag.objects.create(name="calm")
        popular = Tag.objects.create(name="popular")
        inexpensive = Tag.objects.create(name="inexpensive")
        caribbean = Tag.objects.create(name="caribbean")
        insider = Tag.objects.create(name="insider")
        ddff = Tag.objects.create(name="dresden-for-friends")

        ascii_cafe = Location.objects.create(
            name="Studentencafé Ascii",
            description="Gemütliches Café in der Fak. Informatik der TU Dresden.",
            address="Nöthnitzer Str. 46, 01187 Dresden",
            user_id=0,

            latitude=Decimal(51.0250869),
            longitude=Decimal(13.7210005),
        )
        ascii_cafe.tags.add(calm, inexpensive, insider)
        ascii_cafe.categories.add(cafe)

        turtle_bay = Location.objects.create(
            name="Turtle Bay Dresden",
            description="Karibisches Restaurant in gemütlicher Atmosphäre "
                        "mit Gerichten aus Trinidad, Jamaika und Martinique.",
            address="Kleine Brüdergasse, 01067 Dresden",
            user_id=0,

            latitude=Decimal(51.0516273),
            longitude=Decimal(13.732316),
        )
        turtle_bay.tags.add(popular, caribbean, ddff)
        turtle_bay.categories.add(restaurant, bar)

        steak_royal = Location.objects.create(
            name="Steak Royal",
            description="Steak-Spezialitäten vom Grill und vieles mehr.",
            address="Weiße Gasse 4, 01067 Dresden",
            user_id=0,

            latitude=Decimal(51.0491),
            longitude=Decimal(13.738407),
        )
        steak_royal.tags.add(popular, calm, ddff)
        steak_royal.categories.add(restaurant)
