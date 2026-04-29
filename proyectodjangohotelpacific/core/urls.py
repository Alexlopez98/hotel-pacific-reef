from django.urls import path
from .views import index_view, login_view, register_view, rooms_view, agregar_habitacion, editar_habitacion

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='registro'), 
    path('habitaciones/', rooms_view, name='habitaciones'),
    
    # Rutas de Gestión
    path('habitaciones/nueva/', agregar_habitacion, name='agregar_habitacion'),
    path('habitaciones/editar/<int:id>/', editar_habitacion, name='editar_habitacion'),
]