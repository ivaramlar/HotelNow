'''
Created on 22 dic 2024

@author: ivanb
'''
import urllib.request
from bs4 import BeautifulSoup
import os, ssl
from urllib.parse import urlparse
from principal.models import Coche, Marca


# Evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    


def extraer_elemento():
    urls = [
        "https://autos.mercadolibre.com.ar/",
        "https://autos.mercadolibre.com.ar/_Desde_48_NoIndex_True",
        "https://autos.mercadolibre.com.ar/_Desde_97_NoIndex_True",
    ]
    pagina_individual_coches = []

    for url in urls:
        try:
            f = urllib.request.urlopen(url)
            s = BeautifulSoup(f, "lxml")
            coches = s.find("ol", class_="ui-search-layout ui-search-layout--grid").find_all("li", class_="ui-search-layout__item")
            for coche in coches:
                url_coches = coche.find("div", class_="poly-card__content")
                if url_coches:
                    url_cochees = url_coches.find("a")["href"]
                    try:
                        f = urllib.request.urlopen(url_cochees)
                        s = BeautifulSoup(f, "lxml")
                        pagina_individual_coches.append(s)
                    except Exception as e:
                        print(f"Error al cargar página del coche: {e}")
        except Exception as e:
            print(f"Error al cargar página principal: {e}")

    return pagina_individual_coches


def almacenar_datos():
    # Limpia las tablas antes de cargar nuevos datos
    Marca.objects.all().delete()
    Coche.objects.all().delete()

    pagina_individual_cochees = extraer_elemento()
    for coche in pagina_individual_cochees:
        try:
            # Extraer datos
            titulo = coche.find("h1").string.strip()
            precio_text = coche.find("span", class_="andes-money-amount__fraction").string.strip()
            precio = float(precio_text.replace(".", ""))
            valores = coche.find("span", class_="ui-pdp-subtitle").string.strip()
            fecha = int(valores.split("|")[0].strip())
            kilometros_text = valores.split("|")[1].split(" ")[1]
            kilometros = int(kilometros_text.replace(".", ""))  # Eliminar los puntos antes de convertir a entero
            marca_nombre = titulo.split(" ")[0]
            descripcion = coche.find("div", class_="ui-pdp-container__row ui-pdp-container__row--description")
            if descripcion:
                descripcion = descripcion.find("p").get_text()
            imagen = coche.find("figure", class_="ui-pdp-gallery__figure").find("img")["data-zoom"]

            # Crear o asociar la marca
            marca, _ = Marca.objects.get_or_create(nombre=marca_nombre)

            # Crear el coche
            Coche.objects.create(
                titulo=titulo,
                precio=precio,
                fecha=fecha,
                kilometros=kilometros,
                descripcion=descripcion,
                imagen=imagen,
                marca=marca
            )
        except Exception as e:
            print(f"Error al procesar los datos del coche: {str(e)}")

    

            
