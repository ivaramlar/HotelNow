#encoding:utf-8
from principal.models import Coche, Marca
from principal.populateDB import almacenar_datos
from principal.CreateWhossIndex import crear_indice

from principal.forms import  UsuarioBusquedaForm, PeliculaBusquedaForm
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.conf import settings
import shelve
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh import query, qparser
from re import search
from whoosh.qparser.default import QueryParser, MultifieldParser
from whoosh.query import And
from whoosh.qparser.syntax import OrGroup
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from principal.forms import  SearchCarByBrandForm, SearchCarByPriceForm, SearchCarByDescriptionForm, SearchCarByTitleForm, CarSelectionForm
from whoosh.query import TermRange, Term
from django.core.paginator import Paginator
from hotel.recommendations import recommend_cars


# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a peliculas. Tambien carga el diccionario inverso
# Serializa los resultados en dataRS.dat

def populateDatabase(request):
    if request.method == "POST":
        almacenar_datos()  # Populate the database
        logout(request)  # Log out the user
        return HttpResponseRedirect('/')  # Redirect to the index page

    # Render a confirmation page if the request is not POST
    return render(request, 'confirm_populate.html')


def ViewBrands(request):
    marcas = Marca.objects.all()
    return render(request, 'view_brands.html', {'marcas': marcas})

def ViewCars(request):
    coches = Coche.objects.all()  # Fetch all cars
    paginator = Paginator(coches, 9)  # Show 9 cars per page

    # Get the current page number from the query parameters
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_cars.html', {'page_obj': page_obj})

def create_index(request):
    if request.method == "POST":
        coches = crear_indice()  # Call the function to create and populate the index
        logout(request)  # Log out the user
        return render(request, 'confirmation_whoos.html', {'data': coches})  # Redirect to the index page
    return render(request, 'confirm_create_index.html')



def search_by_brand_and_title(request):
    selected_brand = None
    title_filter = None
    results = []  # To store the car data
    ix = open_dir("Index")  # Open the Whoosh index

    if request.method == "POST":
        # Combine both forms for brand and title
        brand_form = SearchCarByBrandForm(request.POST)
        title_form = SearchCarByTitleForm(request.POST)

        if brand_form.is_valid() and title_form.is_valid():
            # Get the selected brand and optional title
            selected_brand = brand_form.cleaned_data['brand']
            title_filter = title_form.cleaned_data.get('title')  # Get title, or None if not provided

            # Perform the search
            with ix.searcher() as searcher:
                # Build the base query for the brand
                brand_query = QueryParser("marca", ix.schema).parse(f'"{selected_brand}"')

                # If a title is provided, add it as an additional query
                if title_filter:
                    title_query = QueryParser("titulo", ix.schema).parse(f'"{title_filter}"')
                    combined_query = And([brand_query, title_query])
                else:
                    combined_query = brand_query

                # Execute the search
                whoosh_results = searcher.search(combined_query)

                # Extract data from Whoosh results
                for result in whoosh_results:
                    results.append({
                        "titulo": result["titulo"],
                        "precio": result["precio"],
                        "fecha": result["fecha"],
                        "kilometros": result["kilometros"],
                        "descripcion": result["descripcion"],
                        "marca": result["marca"]
                    })
    else:
        brand_form = SearchCarByBrandForm()
        title_form = SearchCarByTitleForm()

    return render(request, 'search_by_brand_and_title.html', {
        'brand_form': brand_form,
        'title_form': title_form,
        'selected_brand': selected_brand,
        'title_filter': title_filter,
        'cars': results  # Pass the extracted data
    })
    
def search_by_price(request):
    results = []
    filter_type = None
    price = None

    # Open the Whoosh index
    ix = open_dir("Index")

    if request.method == "POST":
        form = SearchCarByPriceForm(request.POST)
        if form.is_valid():
            # Get the filter type and price
            filter_type = form.cleaned_data['filter_type']
            price = float(form.cleaned_data['price'])

            with ix.searcher() as searcher:
                # Build the query based on filter type
                if filter_type == 'lower':
                    query = TermRange("precio", None, price, startexcl=False, endexcl=True)
                elif filter_type == 'higher':
                    query = TermRange("precio", price, None, startexcl=True, endexcl=False)

                # Perform the search
                whoosh_results = searcher.search(query)

                # Extract the data
                for result in whoosh_results:
                    results.append({
                        "titulo": result["titulo"],
                        "precio": result["precio"],
                        "fecha": result["fecha"],
                        "kilometros": result["kilometros"],
                        "descripcion": result["descripcion"],
                        "marca": result["marca"]
                    })
    else:
        form = SearchCarByPriceForm()

    return render(request, 'search_by_price.html', {
        'form': form,
        'filter_type': filter_type,
        'price': price,
        'cars': results
    })


def search_by_description(request):
    results = []  # List to store search results
    query_text = None

    # Open the Whoosh index
    ix = open_dir("Index")

    if request.method == "POST":
        form = SearchCarByDescriptionForm(request.POST)
        if form.is_valid():
            query_text = form.cleaned_data['description']

            # Perform the search
            with ix.searcher() as searcher:
                # Parse the query for the 'descripcion' field
                query = QueryParser("descripcion", ix.schema).parse(query_text)
                whoosh_results = searcher.search(query, limit=20)  # Limit to 20 results

                # Extract data from Whoosh results
                for result in whoosh_results:
                    results.append({
                        "titulo": result["titulo"],
                        "marca": result["marca"],
                        "precio": result["precio"],
                        "fecha": result["fecha"],
                        "kilometros": result["kilometros"],
                        "descripcion": result["descripcion"],
                    })

    else:
        form = SearchCarByDescriptionForm()

    return render(request, 'search_by_description.html', {
        'form': form,
        'query_text': query_text,
        'cars': results
    })



def car_recommendation_view(request):
    cars = Coche.objects.all()
    selected_car = None
    recommendations = []
    form = CarSelectionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        selected_car = form.cleaned_data["car"]

        # Prepare car data
        car_data = [
            {
                "id": car.id,
                "titulo": car.titulo,
                "precio": car.precio,
                "fecha": car.fecha,
                "kilometros": car.kilometros,
                "marca_encoded": car.marca.id if car.marca else 0,
                "descripcion": car.descripcion,

            }
            for car in cars
        ]

        # Find reference car
        reference_car = next(c for c in car_data if c["id"] == selected_car.id)

        # Get recommendations
        recommendations = recommend_cars(car_data, reference_car)

    return render(request, "car_recommendation.html", {
        "form": form,
        "selected_car": selected_car,
        "recommendations": recommendations,
    })