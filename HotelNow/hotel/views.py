from django.shortcuts import render
from hotel.populateDB import almacenar_datos
from django.contrib.auth import login, authenticate, logout
from django.http.response import HttpResponseRedirect
from hotel.models import  Hotel,Tipo
from django.core.paginator import Paginator
from django.http import JsonResponse
from hotel.recommendations import recommend_hotels
from hotel.form import HotelSelectionForm,SearchHotelByDescriptionForm
from hotel.createWhoosIndex import crear_indice_hotel
from whoosh.index import create_in, open_dir
from whoosh import query, qparser
from whoosh.qparser.default import QueryParser, MultifieldParser


# Create your views here.
def populateDatabaseHotel(request):
    if request.method == "POST":
        almacenar_datos()  # Populate the database
        logout(request)  # Log out the user
        return HttpResponseRedirect('/')  # Redirect to the index page

    # Render a confirmation page if the request is not POST
    return render(request, 'confirm_populate.html')


def ViewTypes(request):
    types = Tipo.objects.all()
    return render(request, 'view_types.html', {'types': types})


def ViewHotels(request):
    hotels = Hotel.objects.all()  # Fetch all hotel
    paginator = Paginator(hotels, 5)

    # Get the current page number from the query parameters
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_hotels.html', {'page_obj': page_obj})



def hotel_recommendation_view(request):
    hotels = Hotel.objects.all()
    selected_hotel = None
    recommendations = []
    form = HotelSelectionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        selected_hotel = form.cleaned_data["hotel"]

        # Prepare data for the recommendation engine
        hotel_data = [
            {
                "id": hotel.id,
                "titulo": hotel.titulo,
                "precio": hotel.precio,
                "surface": hotel.surface,
                "bathrooms": hotel.bathrooms,
                "rooms": hotel.rooms,
                "tipo_encoded": hotel.tipo.id if hotel.tipo else 0,
                "descripcion": hotel.descripcion,

            }
            for hotel in hotels
        ]

        # Find reference hotel
        reference_hotel = next(h for h in hotel_data if h["id"] == selected_hotel.id)

        # Get recommendations
        recommendations = recommend_hotels(hotel_data, reference_hotel)

    return render(request, "recommendation.html", {
        "form": form,
        "selected_hotel": selected_hotel,
        "recommendations": recommendations,
    })
    
    
def create_index(request):
    if request.method == "POST":
        hotels = crear_indice_hotel()  # Call the function to create and populate the index
        logout(request)  # Log out the user
        return render(request, 'confirmation_whoos.html', {'data': hotels})  # Redirect to the index page
    return render(request, 'confirm_create_index.html')



def search_by_description(request):
    results = []  # List to store search results
    query_text = None

    # Open the Whoosh index
    ix = open_dir("HotelIndex")

    if request.method == "POST":
        form = SearchHotelByDescriptionForm(request.POST)
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
                        "precio": result["precio"],
                        "precio_alquiler": result["precio_alquiler"],
                        "anyo_construccion": result["anyo_construccion"],
                        "surface": result["surface"],
                        "bathrooms": result["bathrooms"],
                        "rooms": result["rooms"],
                        "tipo": result["tipo"],
                        "descripcion": result["descripcion"],
                    })

    else:
        form = SearchHotelByDescriptionForm()

    return render(request, 'search_hotel_by_description.html', {
        'form': form,
        'query_text': query_text,
        'hotels': results  # Changed from 'cars' to 'hotels'
    })
