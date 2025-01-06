"""
URL configuration for Practica3_AII project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from principal import views
from HotelNow.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('brands/',views.ViewBrands),
    path('cars/',views.ViewCars),
    path('populate/', views.populateDatabase, name='populate_database'),
    path('create_whoos_index/', views.create_index, name='create_index'),
    path('', home, name='home'),
    path('search_car_by_brand_and_title/', views.search_by_brand_and_title, name='select_brand'),
    path('search_by_price/', views.search_by_price, name='search_by_price'),
    path('search_by_description/', views.search_by_description, name='search_by_description'),
    path('recommendation/', views.car_recommendation_view),
    path('hotel/', include('hotel.urls'))


]
