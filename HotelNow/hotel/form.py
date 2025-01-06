'''
Created on 6 ene 2025

@author: ivanb
'''
# forms.py
from django import forms
from .models import Hotel

class HotelSelectionForm(forms.Form):
    hotel = forms.ModelChoiceField(
        queryset=Hotel.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Select a Hotel",
    )
    
    
class SearchHotelByDescriptionForm(forms.Form):
    description = forms.CharField(
        label="Search by Description",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter keywords for description'
        })
    )