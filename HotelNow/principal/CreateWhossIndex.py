from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from principal.models import Coche
import os

def crear_indice():
    # Define the schema for the index
    schema = Schema(
        titulo=TEXT(stored=True),
        precio=NUMERIC(stored=True, decimal_places=2),
        fecha=NUMERIC(stored=True),
        kilometros=NUMERIC(stored=True),
        descripcion=TEXT(stored=True),
        marca=TEXT(stored=True)
    )

    # Ensure the directory for the index exists
    index_dir = "Index"
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    # Create the Whoosh index
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    # Fetch all cars from the database
    coches = Coche.objects.all()

    for coche in coches:
        try:
            # Add each car to the index
            writer.add_document(
                titulo=coche.titulo,
                precio=float(coche.precio),
                fecha=coche.fecha,
                kilometros=coche.kilometros,
                descripcion=coche.descripcion or "",
                marca=coche.marca.nombre
            )
        except Exception as e:
            print(f"Error al cargar los datos del coche: {str(e)}")

    # Commit changes to the index
    writer.commit()
    
    # Output message for the number of cars indexed
    return ix.reader().doc_count()
