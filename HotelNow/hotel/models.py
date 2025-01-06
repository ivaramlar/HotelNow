from django.db import models

# Create your models here.

class Tipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Ensures each type name is unique

    def __str__(self):
        return self.nombre


class Hotel(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.FloatField()
    precio_alquiler = models.FloatField(null=True, blank=True)
    anyo_construccion = models.PositiveIntegerField()
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True)  # Not unique, allows multiple hotels of the same type
    surface = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()

    def __str__(self):
        return self.titulo
