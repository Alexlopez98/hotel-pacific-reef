from django.contrib import admin
from .models import Habitacion, Reserva

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    # Esto controla qué columnas se ven en la lista principal del admin
    list_display = ('numero', 'categoria', 'capacidad', 'precio_diario', 'estado')
    
    # Agrega un buscador por número de habitación o categoría
    search_fields = ('numero', 'categoria')
    
    # Agrega filtros laterales por estado y categoría
    list_filter = ('estado', 'categoria')

# Registramos también las Reservas de forma sencilla
admin.site.register(Reserva)