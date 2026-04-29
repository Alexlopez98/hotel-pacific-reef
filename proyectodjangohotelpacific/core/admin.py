from django.contrib import admin
from .models import Habitacion, Reserva, HabitacionImagen

# --- CONFIGURACIÓN PARA IMÁGENES EXTRA ---
class HabitacionImagenInline(admin.TabularInline):
    """
    Permite subir y editar las 3 imágenes adicionales 
    dentro del mismo formulario de la Habitación.
    """
    model = HabitacionImagen
    extra = 3      # Define que aparezcan los 3 espacios vacíos que solicitaste
    max_num = 10   # Límite máximo de fotos por si decides subir más luego

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista principal
    list_display = ('numero', 'categoria', 'capacidad', 'precio_diario', 'estado')
    
    # Buscador y Filtros
    search_fields = ('numero', 'categoria')
    list_filter = ('estado', 'categoria')
    
    # --- VINCULACIÓN DE LAS SUB-IMÁGENES ---
    # Esto hace que aparezcan los cuadros de carga para las fotos extra
    inlines = [HabitacionImagenInline]

# Registro de Reservas
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'habitacion', 'fecha_ingreso', 'fecha_salida', 'estado_reserva')
    list_filter = ('estado_reserva',)
    search_fields = ('id_usuario',)