'''
Created on 22 dic 2024

@author: ivanb
'''
import urllib.request
from bs4 import BeautifulSoup
import os, ssl
from urllib.parse import urlparse
import json
import random
from hotel.models import Hotel,Tipo
# Evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    


def extraer_elemento():
    base_url = "https://www.tecnocasa.es/venta/inmuebles/comunidad-de-madrid/madrid.html"
    pagina_individual_hoteles = []
    rooms = []
    bathrooms = []
    surfaces = []

    for url in range(1,10):
        try:
            f = urllib.request.urlopen(base_url + "/pag-" + str(url))
            s = BeautifulSoup(f, "lxml")

            # Find all `estate-card` elements
            hoteles = s.find_all("estate-card")  # Use `find_all` to get a list of elements
            
            for hotel in hoteles:
                room = hotel.find("template", {"slot": "estate-rooms"})
                surface = hotel.find("template", {"slot": "estate-surface"})
                bathroom = hotel.find("template", {"slot": "estate-bathrooms"})
                if room: room = room.string.strip().split(" ")[0]
                if surface: surface = surface.string.strip().split(" ")[0]
                if bathroom: bathroom = bathroom.string.strip().split(" ")[0]
                rooms.append(int(room))
                bathrooms.append(int(surface))
                surfaces.append(int(bathroom))
                # Extract the `:estate` attribute
                estate_data = hotel.get(':estate')
                if estate_data:
                    # Parse the JSON data
                    estate_dict = json.loads(estate_data)
                    
                    # Get the detail URL
                    url_hotel = estate_dict.get('detail_url')
                    if url_hotel:
                        #print("Detail URL:", url_hotel)

                        # Open the detail page and parse it
                        try:
                            f = urllib.request.urlopen(url_hotel)
                            detail_soup = BeautifulSoup(f, "lxml")
                            pagina_individual_hoteles.append(detail_soup)
                        except Exception as e:
                            print(f"Error al cargar página del hogar: {e}")
        except Exception as e:
            print(f"Error al cargar página principal: {e}")

    return pagina_individual_hoteles, rooms, surface, bathrooms


def almacenar_datos():
    Tipo.objects.all().delete()
    Hotel.objects.all().delete()
    pagina_individual_hoteles, rooms, bathrooms, surfaces = extraer_elemento()
    
    for index, hotel in enumerate(pagina_individual_hoteles):
        try:
            # Ensure the index is valid for all lists
            room = rooms[index] if index < len(rooms) else 2
            bathroom = bathrooms[index] if index < len(bathrooms) else 1
            surface = surfaces[index] if index < len(surfaces) else 100

            # Extract additional data
            titulo = hotel.find("h1", class_="estate-title").string.strip()
            descripcion_element = hotel.find("template", {"slot": "estate-description"})
            descripcion = descripcion_element.get_text() if descripcion_element else None

            precio_element = hotel.find("template", {"slot": "estate-costs"}).find_all("div", class_="col")
            precio = float(precio_element[1].find("strong").string.strip().split(" ")[0].replace(".", ""))
            precio_alquiler = float(precio_element[3].find("strong").find("div").string.strip().split(" ")[1].replace(".", ""))

            features = hotel.find("template", {"slot": "estate-features"}).find_all("div", class_="col")
            tipo_nombre = features[-3].string.strip()
            anyo_construccion = int(features[-1].string.strip())
            
            # Ensure 'Tipo' exists in the database
            tipos = ["Baja", "Media", "Popular", "De época", "Señorial"]
            for tipo in tipos:
                Tipo.objects.get_or_create(nombre=tipo)

            # Assign a random valid type if the extracted type is not in the list
            if tipo_nombre not in tipos:
                tipo_nombre = random.choice(tipos)

            # Get the 'Tipo' instance
            tipo_instance, created = Tipo.objects.get_or_create(nombre=tipo_nombre)

            # Create and save the 'Hotel' instance
            Hotel.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                precio=precio,
                precio_alquiler=precio_alquiler,
                anyo_construccion=anyo_construccion,
                tipo=tipo_instance,
                rooms=room,
                bathrooms=bathroom,
                surface=surface
            )

        except Exception as e:
            print(f"Error al procesar los datos del hotel: {str(e)}")
        
    

if __name__ == '__main__':
    almacenar_datos()     
