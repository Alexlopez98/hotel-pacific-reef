from django.contrib import admin
from django import forms
from .models import Habitacion, Reserva, HabitacionImagen, Usuario, Pago

# =========================
# USUARIO
# =========================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Admin de usuarios del sistema.
    """
    list_display = ('id_usuario', 'rut', 'nombre', 'correo', 'rol')
    search_fields = ('rut', 'nombre', 'correo')
    list_filter = ('rol',)


# =========================
# HABITACIÓN + IMÁGENES
# =========================
class HabitacionImagenInline(admin.TabularInline):
    """
    Permite agregar múltiples imágenes dentro del admin de Habitacion.
    """
    model = HabitacionImagen
    extra = 3       # Muestra 3 campos vacíos por defecto
    max_num = 10    # Máximo de imágenes permitidas


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    """
    Admin de Habitaciones:
    - listado con info clave
    - filtros por estado y categoría
    - soporte para imágenes adicionales
    """
    list_display = ('numero', 'categoria', 'capacidad', 'precio_diario', 'estado')
    search_fields = ('numero', 'categoria')
    list_filter = ('estado', 'categoria')
    inlines = [HabitacionImagenInline]


# =========================
# RESERVA
# =========================
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Admin de reservas del sistema.
    """
    list_display = (
        'id_reserva',
        'habitacion',
        'fecha_ingreso',
        'fecha_salida',
        'estado_reserva'
    )
    list_filter = ('estado_reserva',)
    search_fields = ('id_reserva',)

# =========================
# FORMULARIO PERSONALIZADO DE PAGO
# =========================
class PagoAdminForm(forms.ModelForm):
    """
    Validación del formulario de Pago antes de guardar en la base de datos.
    Evita errores de integridad (ej: reservas inexistentes).
    """

    class Meta:
        model = Pago
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        reserva = cleaned_data.get('id_reserva')

        # -------------------------
        # Validación: reserva vacía
        # -------------------------
        if not reserva:
            self.add_error('id_reserva', "Debes seleccionar una reserva.")
            return cleaned_data

        # -------------------------
        # Validación: existencia real en BD
        # -------------------------
        reserva_id = getattr(reserva, 'id_reserva', reserva)

        if not Reserva.objects.filter(id_reserva=reserva_id).exists():
            self.add_error(
                'id_reserva',
                f"❌ La reserva ID {reserva_id} no existe en el sistema."
            )

        return cleaned_data


# =========================
# PAGO
# =========================
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """
    Admin de pagos:
    - usa validación personalizada
    - evita errores de integridad
    """
    form = PagoAdminForm

    list_display = (
        'id_pago',
        'id_reserva',
        'monto_pagado',
        'metodo_pago',
        'fecha_pago'
    )

    search_fields = ('id_reserva__id_reserva',)