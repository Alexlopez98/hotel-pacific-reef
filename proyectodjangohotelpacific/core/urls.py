from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='registro'),
    path('habitaciones/', views.rooms_view, name='habitaciones'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('habitacion/<int:hab_id>/', views.room_detail, name='roomdetail'),

    path('reservar/provisional/<int:id_habitacion>/', views.crear_reserva_provisional, name='crear_reserva_provisional'),

    path('reservar/confirmar/<int:id_reserva>/', views.confirmar_pago_final, name='confirmar_pago_final'),

    path('habitaciones/nueva/', views.agregar_habitacion, name='agregar_habitacion'),

    path('habitaciones/editar/<int:id>/', views.editar_habitacion, name='editar_habitacion'),

    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    
    path('confirmar-pago/<int:id_reserva>/<int:id_habitacion>/', views.confirmar_pago_final, name='confirmar_pago_final'),
]