#encoding:utf-8
from django import forms
from principal.models import Marca, Coche
from django.core.exceptions import ValidationError

class UsuarioBusquedaForm(forms.Form):
    idUsuario = forms.CharField(label="Id de Usuario", widget=forms.TextInput, required=True)
    
class PeliculaBusquedaForm(forms.Form):
    idPelicula = forms.CharField(label="Id de Pelicula", widget=forms.TextInput, required=True)
    
class SearchCarByBrandForm(forms.Form):
    brand = forms.ModelChoiceField(
        queryset= Marca.objects.all(),
        label="Select a brand",
        empty_label="Choose a brand",  # Placeholder for the dropdown
               widget=forms.Select(attrs={'class': 'form-control'})  # Add Bootstrap styling
               )
    
    
class SearchCarByTitleForm(forms.Form):
    title = forms.CharField(
        label="Search by Title",
        max_length=255,
        required=False,  # Title is optional
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter title (optional)'
        })
    )

FILTER_CHOICES = [
        ('lower', 'Lower than'),
        ('higher', 'Higher than'),
    ]    

class SearchCarByPriceForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES,
        label="Filter Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        label="Price",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'})
    )
    
    def clean_price(self):
            price = self.cleaned_data.get('price')
            if price is not None and price < 0:
                raise ValidationError("Price must be a non-negative value.")
            return price
        
        
class SearchCarByDescriptionForm(forms.Form):
    description = forms.CharField(
        label="Search by Description",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter keywords for description'
        })
    )
    
class CarSelectionForm(forms.Form):
    car = forms.ModelChoiceField(
        queryset=Coche.objects.all(),
        empty_label="Select a car",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Choose a car"
    )