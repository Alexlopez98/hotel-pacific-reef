from django.urls import path
from .views import (
    index_view, login_view, register_view, rooms_view, 
    agregar_habitacion, editar_habitacion, room_detail, 
    crear_reserva_provisional, confirmar_pago_final # <-- Asegúrate de importar las nuevas
)

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='registro'), 
    path('habitaciones/', rooms_view, name='habitaciones'),
    
    # Detalle de la habitación
    path('habitacion/<int:hab_id>/', room_detail, name='roomdetail'),

    # 1. PASO INTERMEDIO: Esta es la que procesa el calendario y manda a pago.html
    # Cambiamos 'crear_reserva' por una que valide y redirija al pago
    path('reservar/provisional/<int:id_habitacion>/', crear_reserva_provisional, name='crear_reserva_provisional'),

    # 2. PASO FINAL: Esta es la que usa el botón "PAGAR" en pago.html para guardar en la BD
    path('reservar/confirmar/<int:id_reserva>/', confirmar_pago_final, name='confirmar_pago_final'),
    
    # Rutas de Gestión
    path('habitaciones/nueva/', agregar_habitacion, name='agregar_habitacion'),
    path('habitaciones/editar/<int:id>/', editar_habitacion, name='editar_habitacion'),
]