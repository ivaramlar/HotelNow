from django.db import models

class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ensure unique names for Marca

    def __str__(self):
        return self.nombre

class Coche(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.IntegerField()
    kilometros = models.PositiveIntegerField()
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.URLField()
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)  # No unique constraint here

    def __str__(self):
        return f"{self.titulo} - {self.marca.nombre}"
