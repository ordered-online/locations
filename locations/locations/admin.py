from django.contrib import admin
from .models import Category, Tag, Location


for model in [Category, Tag, Location]:
    admin.site.register(model)
