'''
Created on 3 ene 2025

@author: ivanb
'''
from django.urls import path
from hotel import views

urlpatterns = [
    path('populate/', views.populateDatabaseHotel),
    path('view_types/', views.ViewTypes),
    path('view_hotels/', views.ViewHotels),
    path('recommendation/', views.hotel_recommendation_view),
    path('create_whoos_index/', views.create_index),
    path('search_hotel_by_description/', views.search_by_description),








]