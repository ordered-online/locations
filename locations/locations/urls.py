"""locations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('locations/find/', views.find_locations, name="find_location"),
    path('locations/nearby/', views.find_nearby_locations, name="find_nearby_locations"),
    path('locations/get/<location_id>/', views.get_location, name="get_location"),
    path('locations/create/', views.create_location, name="create_location"),
    path('locations/edit/<location_id>/', views.edit_location, name="edit_location"),
]
