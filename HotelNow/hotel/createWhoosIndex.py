'''
Created on 6 ene 2025

@author: ivanb
'''
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from hotel.models import Hotel
import os

def crear_indice_hotel():
    # Define the schema for the index
    schema = Schema(
        titulo=TEXT(stored=True),
        descripcion=TEXT(stored=True),
        precio=NUMERIC(stored=True, decimal_places=2),
        precio_alquiler=NUMERIC(stored=True, decimal_places=2),
        anyo_construccion=NUMERIC(stored=True),
        surface=NUMERIC(stored=True),
        bathrooms=NUMERIC(stored=True),
        rooms=NUMERIC(stored=True),
        tipo=TEXT(stored=True)
    )

    # Ensure the directory for the index exists
    index_dir = "HotelIndex"
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    # Create the Whoosh index
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    # Fetch all hotels from the database
    hoteles = Hotel.objects.all()

    for hotel in hoteles:
        try:
            # Add each hotel to the index
            writer.add_document(
                titulo=hotel.titulo,
                descripcion=hotel.descripcion or "",
                precio=float(hotel.precio),
                precio_alquiler=float(hotel.precio_alquiler) if hotel.precio_alquiler else 0.0,
                anyo_construccion=hotel.anyo_construccion,
                surface=hotel.surface,
                bathrooms=hotel.bathrooms,
                rooms=hotel.rooms,
                tipo=hotel.tipo.nombre if hotel.tipo else "Unknown"
            )
        except Exception as e:
            print(f"Error al cargar los datos del hotel: {str(e)}")

    # Commit changes to the index
    writer.commit()
    
    # Output message for the number of hotels indexed
    return ix.reader().doc_count()
